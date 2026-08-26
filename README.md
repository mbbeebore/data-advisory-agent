# DMA Agent — Ingestion Prototype

A prototype for the Data Management Advisory (DMA) Agent: automates the early
intake steps of a DMA case — reading a Jira ticket, extracting the fields the
DMA team needs, and preparing a structured case record — while every
governance decision stays with the human advisory team.

**This repository currently covers ingestion only.** No AI model is called
anywhere in this code yet — everything here is deterministic field extraction
and mapping. That's intentional: this is Stage 1 (Intake) and Stage 2
(Ingestion) of a five-stage design, and both are rule-based by design. Stages
3–5 (building a unified profile, drafting an assessment, detecting gaps) come
later, once this foundation is proven reliable.

---

## Current status

| Piece | Status |
|---|---|
| Jira connection (self-hosted, Personal Access Token) | Working |
| Ticket field extraction, organized by category | Working |
| Field discovery tool (maps custom field IDs to names) | Working |
| New-ticket detection (polling, no webhook) | Working |
| LeanIX lookup | Stubbed — needs the LeanIX ID field mapped via discovery |
| Colibri lookup | Blocked — no API or MCP server available yet |
| Case storage | Local JSON files (moves to a real database later) |
| Automatic triggering (webhook) | Not built — this still runs manually or via polling |

---

## Project structure

```
.env                    Your real credentials — never committed (see below)
.env.example             Template showing what .env needs to contain
requirements.txt         Python dependencies

discover_fields.py        Run this first — finds custom field IDs on a real ticket
test_jira_connection.py   Quick check that your token and URL actually work

dma_mvp/
  jira_client.py          Talks to Jira: fetches raw ticket data
  field_mapping.py         Maps raw Jira fields into the organized CaseFile schema
                            (FIELD_ID_MAP lives here — see "Configuring your fields")
  leanix_client.py          Talks to LeanIX (GraphQL, with token exchange)
  casefile.py               Builds and saves the structured case record
  main.py                    Ties it all together — run this to process one ticket

poll_new_tickets.py       Watches for new tickets without needing a webhook
```

---

## Setup

1. **Clone the repo and create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Create your `.env` file** (copy `.env.example` and fill in real values):
   ```
   JIRA_BASE_URL=https://devstack.vwgroup.com/jira
   JIRA_PAT=your-personal-access-token
   LEANIX_BASE_URL=https://your-workspace.leanix.net
   LEANIX_API_TOKEN=your-leanix-api-token
   ```
   Get your Jira token from your Jira profile → Personal Access Tokens →
   Create token. It inherits exactly your own permissions — there's no
   separate access request.

   **`.env` is in `.gitignore` and must never be committed.** If you ever
   suspect a real token has been pushed, treat it as compromised and
   generate a new one — don't just delete the file in a later commit,
   since the old commit still has it in history.

---

## Running it, in order

**1. Confirm the connection works:**
```bash
python test_jira_connection.py
```
Should print `SUCCESS - token is valid` and your own username.

**2. Discover your custom field IDs** (only needs to happen once, or whenever
you need to map a new field):
```bash
python discover_fields.py
```
Edit the ticket key at the bottom of the file to a real, well-filled-out
ticket first. This prints every non-empty field on that ticket with its ID,
label, and current value — use it to find the real `customfield_XXXXX` ID
behind things like Business Domain, Colibri URL, Data Consumer, etc.

**3. Process a real ticket:**
```bash
cd dma_mvp
python main.py
```
Edit the ticket key at the bottom of `main.py` first. Output is saved to
`dma_mvp/casefiles/<TICKET-KEY>.json` — open it to see the full structured
record.

**4. Test live ingestion** (watches for new tickets without a webhook):
```bash
python poll_new_tickets.py
```
Leave it running, then create a test ticket in Jira. It should appear in the
terminal within a minute, and get logged to `ingested_tickets.csv`.

---

## Configuring your fields

All custom field mapping lives in **one place**: `FIELD_ID_MAP` at the top of
`dma_mvp/field_mapping.py`. After running `discover_fields.py`, copy each
field ID you find into this dictionary:

```python
FIELD_ID_MAP = {
    "colibri_url": "customfield_10087",
    "business_domain": "customfield_10112",
    "data_consumer": "customfield_10130",
    ...
}
```

Anything left as `None` just returns `None` when extracted, rather than
failing — so fields can be filled in one at a time as they're found.

---

## Known limitations / not yet built

- **Colibri integration is blocked.** No API or MCP server exists yet;
  the only identified path is a Gravity export. `map_colibri()` is a stub
  until this is resolved.
- **LeanIX ID field isn't wired up yet.** The Jira custom field holding the
  LeanIX ID needs to be found via `discover_fields.py` and added to
  `FIELD_ID_MAP` before the LeanIX lookup in `main.py` will do anything.
- **No webhook.** `poll_new_tickets.py` proves the ingestion logic works,
  but only while it's running on your machine. Automatic, always-on
  triggering requires deploying this behind an Azure Function later.
- **No database yet.** Case files are local JSON, intended for development
  only — this moves to a real database (Azure Database for PostgreSQL) once
  the extraction logic is proven against enough real tickets.
- **No AI model integration.** Stages 3–5 (profile building, assessment
  drafting, gap detection) aren't started — this repo is intake and
  ingestion only.

---

## Security

- Never commit `.env`. Only `.env.example` (with placeholder values) belongs
  in the repository.
- Your Jira PAT and LeanIX API token both inherit your own personal access —
  treat them like a password.
- If a real token ever ends up in a commit, rotate it immediately. Deleting
  the file in a later commit does not remove it from git history.
