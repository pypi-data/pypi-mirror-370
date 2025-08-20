from typing import Optional, Dict, Any, List
import os
import requests
from ..models import Lead


def _token() -> Optional[str]:
    return os.getenv("HUBSPOT_ACCESS_TOKEN")


def _headers() -> Dict[str, str]:
    token = _token()
    if not token:
        raise RuntimeError("HUBSPOT_ACCESS_TOKEN not set")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def _search_contact_by_twitterhandle(handle: str) -> Optional[str]:
    try:
        h = _headers()
    except Exception:
        return None
    url = "https://api.hubapi.com/crm/v3/objects/contacts/search"
    body = {
        "filterGroups": [
            {
                "filters": [
                    {
                        "propertyName": "twitterhandle",
                        "operator": "EQ",
                        "value": handle,
                    }
                ]
            }
        ],
        "limit": 1,
        "properties": ["twitterhandle"],
    }
    resp = requests.post(url, headers=h, json=body, timeout=15)
    if resp.status_code == 401:
        return None
    resp.raise_for_status()
    results = resp.json().get("results", [])
    if not results:
        return None
    return results[0].get("id")


def _create_contact(props: Dict[str, Any]) -> Optional[str]:
    try:
        h = _headers()
    except Exception:
        return None
    url = "https://api.hubapi.com/crm/v3/objects/contacts"
    resp = requests.post(url, headers=h, json={"properties": props}, timeout=15)
    if resp.status_code == 401:
        return None
    resp.raise_for_status()
    return resp.json().get("id")


def _update_contact(contact_id: str, props: Dict[str, Any]) -> bool:
    try:
        h = _headers()
    except Exception:
        return False
    url = f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}"
    resp = requests.patch(url, headers=h, json={"properties": props}, timeout=15)
    if resp.status_code == 401:
        return False
    resp.raise_for_status()
    return True


def _split_name(name: Optional[str]) -> Dict[str, str]:
    if not name:
        return {"firstname": "", "lastname": ""}
    parts = name.strip().split()
    if len(parts) == 1:
        return {"firstname": parts[0], "lastname": ""}
    return {"firstname": parts[0], "lastname": " ".join(parts[1:])}


def save_leads_to_hubspot(leads: List[Lead]) -> int:
    """
    Create or update contacts in HubSpot using the default contact property 'twitterhandle'.
    Requires HUBSPOT_ACCESS_TOKEN with contacts read/write scopes.
    """
    if not _token():
        return len(leads)
    saved = 0
    for lead in leads:
        tw = (lead.handle or "").lstrip("@")
        name_parts = _split_name(lead.name)
        props = {
            "twitterhandle": tw,
            "lifecyclestage": "lead",
            "firstname": name_parts["firstname"],
            "lastname": name_parts["lastname"],
        }
        # Attempt upsert by twitterhandle search
        cid = _search_contact_by_twitterhandle(tw)
        if cid:
            ok = _update_contact(cid, props)
            if ok:
                saved += 1
        else:
            created = _create_contact(props)
            if created:
                saved += 1
    return saved


