"""
The CaseFile - one JSON file per project, for now.

Moves to Postgres once this is running in Azure. Local JSON is enough to
prove the logic works, and it's easy to open and eyeball while debugging -
especially useful now that the intake record has real structure to check.
"""

import json
import os
from datetime import datetime, timezone

CASEFILE_DIR = "casefiles"


def new_casefile(jira_intake: dict) -> dict:
    return {
        "issue_key": jira_intake["identification"]["issue_key"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "jira": jira_intake,
        "leanix": None,
        "colibri": None,
        "status": "intake_complete",
    }


def save(casefile: dict) -> str:
    os.makedirs(CASEFILE_DIR, exist_ok=True)
    path = os.path.join(CASEFILE_DIR, f"{casefile['issue_key']}.json")
    with open(path, "w") as f:
        json.dump(casefile, f, indent=2)
    return path
