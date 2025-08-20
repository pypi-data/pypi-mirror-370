from typing import List, Dict, Any

try:
    from pyairtable import Table  # type: ignore
except Exception:  # pragma: no cover
    Table = None  # fallback when not installed

from ..config import settings


def _get_table(name: str):
    if not settings.airtable.api_key or not settings.airtable.base_id:
        return None
    if Table is None:
        return None
    return Table(settings.airtable.api_key, settings.airtable.base_id, name)


def save_healthcare_insights(summary: str, insights: List[Dict[str, Any]]) -> int:
    """
    Save insights into Airtable table defined by AIRTABLE_TABLE_HEALTHCARE_INSIGHTS.
    Each record maps common fields; missing fields are defaulted.
    Returns number of records attempted.
    """
    table = _get_table(settings.airtable.tables.healthcare_insights)
    if table is None:
        return len(insights)

    to_create = []
    for ins in insights:
        fields = {
            "TweetId": str(ins.get("tweetId", "")),
            "Author": str(ins.get("author", "")),
            "Text": str(ins.get("text", ""))[:5000],
            "IsHealthcareRelated": bool(ins.get("isHealthcareRelated", False)),
            "IsUKRelated": bool(ins.get("isUKRelated", False)),
            "Categories": ", ".join(ins.get("categories", []) or []),
            "PainPoints": ", ".join(ins.get("painPoints", []) or []),
            "Sentiment": str(ins.get("sentiment", "")),
            "Urgency": float(ins.get("urgency", 0) or 0),
            "Relevance": float(ins.get("relevance", 0) or 0),
            "Contacts": ", ".join(ins.get("contacts", []) or []),
            "Summary": summary,
        }
        to_create.append({"fields": fields})

    # Airtable API limit: create up to 10 per request
    for i in range(0, len(to_create), 10):
        batch = to_create[i : i + 10]
        table.batch_create(batch, typecast=True)

    return len(insights)


