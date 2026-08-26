"""
The whole MVP, run manually against one ticket to start.

Flow: Jira ticket -> extract organized intake fields -> look up LeanIX ->
save case file. Colibri stays stubbed until access is unblocked.
"""

from dotenv import load_dotenv
load_dotenv()

import jira_client
import leanix_client
import field_mapping
import casefile


def process_ticket(issue_key: str):
    print(f"Fetching {issue_key} from Jira...")
    jira_raw = jira_client.get_ticket(issue_key)
    intake = field_mapping.extract_case_intake(jira_raw)

    ident = intake["identification"]
    print(f"  Project: {ident['project_name']}")
    print(f"  Project URL: {ident['project_url']}")
    print(f"  Colibri URL: {ident['colibri_url']}")
    print(f"  Business domain: {intake['classification']['business_domain']}")
    print(f"  Involved systems: {intake['systems']['involved_systems']}")

    leanix_raw = None
    # LeanIX lookup still needs a LeanIX ID - wire this up once you've found
    # which custom field holds it via discover_fields.py, same pattern as
    # the fields above.

    case = casefile.new_casefile(intake)
    case["leanix"] = field_mapping.map_leanix(leanix_raw)
    case["colibri"] = field_mapping.map_colibri(None)

    path = casefile.save(case)
    print(f"Case file saved: {path}")


if __name__ == "__main__":
    process_ticket("DMYJSM-1")  # replace with a real ticket key to test
