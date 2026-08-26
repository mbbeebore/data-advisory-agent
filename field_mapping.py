"""
The source-to-target data mapping.

This is where every raw Jira field lands in the shared CaseFile schema,
organized into clearly labeled groups rather than one flat list - so
"where does the business domain come from?" always has one obvious answer.

HOW TO WIRE UP YOUR REAL FIELDS:
Run discover_fields.py against a real, well-filled ticket first. It prints
every field's ID next to its label and current value. Copy the IDs you find
into FIELD_ID_MAP below - that's the only place you should ever need to
change. Anything left as None just returns None when extracted, instead of
crashing - so you can fill these in one at a time as you find them, and
everything else keeps working in the meantime.
"""

import os

JIRA_BASE_URL = os.environ.get("JIRA_BASE_URL", "")

# Fill these in using discover_fields.py. Leave as None until you've found
# the real ID - extraction handles missing ones gracefully.
FIELD_ID_MAP = {
    "colibri_url": None,             # e.g. "customfield_10087"
    "business_domain": None,
    "product_timeline": None,
    "business_owner": None,
    "data_consumer": None,
    "additional_contacts": None,
    "involved_systems": None,
    "data_shopping_process": None,   # kept as you named it - confirm this is the right
                                      # field during discovery; rename the key here if not
    "short_description": None,       # only if distinct from the ticket summary
}


def _get_custom(fields: dict, key: str):
    """Looks up FIELD_ID_MAP[key] and pulls that field's value, or None
    if the ID hasn't been filled in yet or the field itself is empty."""
    field_id = FIELD_ID_MAP.get(key)
    if not field_id:
        return None
    return fields.get(field_id)


def extract_case_intake(raw_ticket: dict) -> dict:
    """
    Pulls every field the DMA case needs from a raw Jira ticket, organized
    into the groups a human reviewer would actually think in terms of.
    """
    fields = raw_ticket.get("fields", {})
    issue_key = raw_ticket["key"]

    return {
        "identification": {
            "issue_key": issue_key,
            "project_name": (fields.get("project") or {}).get("name"),
            "project_url": f"{JIRA_BASE_URL}/browse/{issue_key}",
            "colibri_url": _get_custom(fields, "colibri_url"),
        },
        "description": {
            "short_description": _get_custom(fields, "short_description") or fields.get("summary"),
            "long_description": fields.get("description"),
        },
        "classification": {
            "business_domain": _get_custom(fields, "business_domain"),
        },
        "timeline": {
            "product_timeline": _get_custom(fields, "product_timeline"),
        },
        "people": {
            "reporter": (fields.get("reporter") or {}).get("displayName"),
            "business_owner": _get_custom(fields, "business_owner"),
            "data_consumer": _get_custom(fields, "data_consumer"),
            "additional_contacts": _get_custom(fields, "additional_contacts"),
        },
        "systems": {
            "involved_systems": _get_custom(fields, "involved_systems"),
        },
        "process": {
            "data_shopping_process": _get_custom(fields, "data_shopping_process"),
        },
    }


def map_leanix(raw_factsheet: dict | None) -> dict:
    """Turn a raw LeanIX fact sheet into CaseFile-shaped fields."""
    if not raw_factsheet:
        return {"lifecycle": None, "application_name": None}
    return {
        "lifecycle": raw_factsheet.get("lifecycle"),
        "application_name": raw_factsheet.get("name"),
    }


def map_colibri(raw_colibri: dict | None) -> dict:
    """Stub until Colibri access is unblocked."""
    return {"owner": None, "data_domain": None}
