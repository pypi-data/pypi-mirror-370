from typing import List
import csv
import os
from .models import HealthcareInsight, HealthcareAnalysis, Lead
from .config import settings
from .services.airtable import _get_table  # reuse internal helper
from .services.airtable import save_healthcare_insights


def save_healthcare_to_csv(path: str, analysis: HealthcareAnalysis) -> int:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    wrote_header = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if wrote_header:
            w.writerow([
                "TweetId","Author","Text","IsHealthcareRelated","IsUKRelated","Categories","PainPoints","Sentiment","Urgency","Relevance","Contacts","Summary"
            ])
        count = 0
        for ins in analysis.insights:
            w.writerow([
                ins.tweetId, ins.author, ins.text, ins.isHealthcareRelated, ins.isUKRelated,
                ", ".join(ins.categories), ", ".join(ins.painPoints), ins.sentiment,
                ins.urgency, ins.relevance, ", ".join(ins.contacts), analysis.summary,
            ])
            count += 1
    return count


def save_healthcare_to_sqlite(db_path: str, analysis: HealthcareAnalysis, table: str = "healthcare_insights") -> int:
    try:
        import sqlite3  # lazy import to avoid hard dependency at runtime
    except Exception as e:
        raise RuntimeError("sqlite3 module not available in your Python build. Install a Python with SQLite support or choose CSV/Airtable storage.") from e
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {table} (
            TweetId TEXT,
            Author TEXT,
            Text TEXT,
            IsHealthcareRelated INTEGER,
            IsUKRelated INTEGER,
            Categories TEXT,
            PainPoints TEXT,
            Sentiment TEXT,
            Urgency REAL,
            Relevance REAL,
            Contacts TEXT,
            Summary TEXT
        )
    """)
    rows = [(
        ins.tweetId, ins.author, ins.text,
        1 if ins.isHealthcareRelated else 0,
        1 if ins.isUKRelated else 0,
        ", ".join(ins.categories), ", ".join(ins.painPoints), ins.sentiment,
        ins.urgency, ins.relevance, ", ".join(ins.contacts), analysis.summary,
    ) for ins in analysis.insights]
    cur.executemany(f"INSERT INTO {table} VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", rows)
    conn.commit()
    conn.close()
    return len(rows)


def save_healthcare_analysis(target: str, analysis: HealthcareAnalysis) -> int:
    """
    target formats:
      - airtable
      - csv:/path/to/file.csv
      - sqlite:/path/to/db.sqlite[::table_name]
    Returns number of records attempted.
    """
    if target == "airtable":
        return save_healthcare_insights(analysis.summary, [ins.model_dump() for ins in analysis.insights])
    if target.startswith("csv:"):
        return save_healthcare_to_csv(target.split(":", 1)[1], analysis)
    if target.startswith("sqlite:"):
        rest = target.split(":", 1)[1]
        if "::" in rest:
            db, table = rest.split("::", 1)
        else:
            db, table = rest, "healthcare_insights"
        return save_healthcare_to_sqlite(db, analysis, table)
    raise ValueError("Unknown storage target")


def save_leads_to_csv(path: str, leads: list[Lead]) -> int:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    wrote_header = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if wrote_header:
            w.writerow(["Handle","Name","SourceTweetId","Relevance","Notes"])
        for l in leads:
            w.writerow([l.handle, l.name or "", l.sourceTweetId or "", l.relevance, l.notes or ""])
    return len(leads)


def save_leads_to_airtable(leads: list[Lead]) -> int:
    table = _get_table(settings.airtable.tables.leads)
    if table is None:
        return len(leads)
    records = []
    for l in leads:
        fields = {
            "Handle": l.handle,
            "Name": l.name or "",
            "SourceTweetId": l.sourceTweetId or "",
            "Relevance": l.relevance,
            "Notes": l.notes or "",
        }
        records.append({"fields": fields})
    for i in range(0, len(records), 10):
        table.batch_create(records[i:i+10], typecast=True)
    return len(leads)


