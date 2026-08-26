"""
Run this once against a real, well-filled-out ticket to find the
customfield_XXXXX ID behind every field you care about.

There's no way to know these IDs in advance - they're generated per Jira
instance. This prints every field that actually has a value, with its ID
and label side by side, so you can scan down the list and match each one
to what you're looking for (Business Domain, Colibri URL, etc.).

Pick a ticket where as many of your target fields as possible are actually
filled in - an empty field won't show up here at all, since there's
nothing to distinguish it from an unused one.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

JIRA_BASE_URL = os.environ["JIRA_BASE_URL"]
JIRA_TOKEN = os.environ["JIRA_PAT"]


def headers():
    return {"Authorization": f"Bearer {JIRA_TOKEN}", "Accept": "application/json"}


def discover(issue_key: str):
    url = f"{JIRA_BASE_URL}/rest/api/2/issue/{issue_key}"
    resp = requests.get(url, headers=headers(), params={"expand": "names"}, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    names = data.get("names", {})
    fields = data["fields"]

    print(f"\nNon-empty fields on {issue_key}:")
    print("-" * 95)
    print(f"{'FIELD ID':<22} {'LABEL':<35} VALUE")
    print("-" * 95)

    for field_id, value in fields.items():
        if value in (None, "", [], {}):
            continue  # skip empty fields - far easier to scan the ones that matter
        label = names.get(field_id, "(no label)")
        preview = str(value)
        if len(preview) > 85:
            preview = preview[:85] + "..."
        print(f"{field_id:<22} {label:<35} {preview}")

    print("-" * 95)
    print("\nFound what you need? Copy each customfield_XXXXX into FIELD_ID_MAP in field_mapping.py")


if __name__ == "__main__":
    discover("DMYJSM-1")  # replace with a real, well-filled-out ticket key
