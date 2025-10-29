from __future__ import annotations
import time
from datetime import datetime, timedelta, timezone
from dateutil import parser as dtparse
from email.utils import parsedate_to_datetime
from typing import Optional, Iterable, Dict
from googleapiclient.discovery import build
from sqlalchemy import create_engine, text
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import dotenv
import os

dotenv.load_dotenv()
ACCOUNTS = [
    {"account_email": os.getenv("IMAP_USER_1"), "imap_user": os.getenv("IMAP_USER_1"), "imap_pass": os.getenv("IMAP_PASS_1")},
    {"account_email": os.getenv("IMAP_USER_2"), "imap_user": os.getenv("IMAP_USER_2"), "imap_pass": os.getenv("IMAP_PASS_2")},
]

# --------------------------------------------
# DB helpers
# --------------------------------------------
DDL = """
CREATE TABLE IF NOT EXISTS job_emails (
  account_email TEXT NOT NULL,
  message_id TEXT NOT NULL,
  date TIMESTAMPTZ NOT NULL,
  title TEXT,
  sender TEXT,
  inserted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (account_email, message_id)
);
"""
#    ALTER TABLE job_emails DROP CONSTRAINT job_emails_pkey;
#    ALTER TABLE job_emails ADD PRIMARY KEY (message_id, account);

UPSERT = """
INSERT INTO job_emails (account, message_id, date, title, sender)
VALUES (:account, :message_id, :date, :title, :sender)
ON CONFLICT (account, message_id) DO NOTHING;
"""
MAX_DATE_SQL = "SELECT MAX(date) AS max_date FROM job_emails where account='{acc}';"
TOKEN_PATH = "gmail_token.json"
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def get_gmail_service(client_secret_path="client_secret_dektop.json", token_path="token.json"):
    creds = None

    # Load existing token if available
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # If no valid token, launch browser to authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            from google.auth.transport.requests import Request
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, SCOPES)
            creds = flow.run_local_server(port=5000)  # opens a browser for you to log in

        # Save the token for next time
        with open(token_path, "w") as token_file:
            token_file.write(creds.to_json())

    # Build the Gmail service
    service = build("gmail", "v1", credentials=creds)
    return service

def init_db(db_url: str):
    engine = create_engine(db_url, future=True)
    with engine.begin() as conn:
        conn.execute(text(DDL))
    return engine

def get_service_with_token(token_path: str):
    creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(token_path, "w") as f: f.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)

def get_account_email(service) -> str:
    # Uses Gmail profile endpoint to get the email address tied to this token
    prof = service.users().getProfile(userId="me").execute()
    return prof["emailAddress"]

def gmail_query(after_dt: datetime, before_dt: datetime) -> str:
    core = """
      (
        from:(linkedin.com OR indeed.com OR greenhouse.io OR lever.co OR icims.com OR jobvite.com OR workday.com OR donotreply@cardmessage.capitalone.com)
        OR subject:(application OR interview OR offer OR regret OR rejection OR opportunity
                    OR "thank you for applying" OR "we appreciate your interest" OR "we regret to inform")
      )
    """.replace("\n"," ").strip()
    after = after_dt.strftime("%Y/%m/%d")
    before = (before_dt + timedelta(days=1)).strftime("%Y/%m/%d")
    return f"{core} after:{after} before:{before} -in:spam"

def get_resume_start(engine, fallback_start: datetime) -> datetime:
    with engine.begin() as conn:
        row = conn.execute(text(MAX_DATE_SQL.format(acc=ACCOUNT))).mappings().first()
    if row and row["max_date"]:
        # resume one minute after last stored email to avoid duplicates in same minute
        return row["max_date"].astimezone(timezone.utc) + timedelta(minutes=1)
    return fallback_start

def store_batch(engine, rows: Iterable[Dict]):
    if not rows:
        return 0
    with engine.begin() as conn:
        conn.execute(text(UPSERT), list(rows))
    return len(rows)

# --------------------------------------------
# Gmail helpers
# --------------------------------------------
def _get_header(headers, name: str) -> Optional[str]:
    for h in headers:
        if h.get("name", "").lower() == name.lower():
            return h.get("value")
    return None

def _parse_gmail_date(date_header: Optional[str]) -> Optional[datetime]:
    """Parse RFC2822 Date into timezone-aware UTC datetime."""
    if not date_header:
        return None
    try:
        dt = parsedate_to_datetime(date_header)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        try:
            # fallback
            return dtparse.parse(date_header).astimezone(timezone.utc)
        except Exception:
            return None

def _gmail_query(start_dt: datetime, end_dt: datetime) -> str:
    # Gmail uses YYYY/MM/DD; 'before:' is exclusive, so add +1 day
    q_core = """
        (
          from:(linkedin.com OR indeed.com OR greenhouse.io OR lever.co OR icims.com OR jobvite.com OR workday.com OR donotreply@cardmessage.capitalone.com)
          OR subject:(application OR interview OR offer OR regret OR rejection OR opportunity
                       OR "thank you for applying"
                       OR "we appreciate your interest"
                       OR "we regret to inform")
        )
    """.replace("\n", " ").strip()
    after = start_dt.strftime("%Y/%m/%d")
    before = (end_dt + timedelta(days=1)).strftime("%Y/%m/%d")
    return f"{q_core} after:{after} before:{before} -in:spam"


def _list_message_ids(service, q: str, max_results: int):
    """Page through Gmail results up to max_results ids."""
    user_id = "me"
    page_token = None
    fetched = 0
    ids = []
    while True:
        batch_size = min(500, max_results - fetched) if max_results else 500
        resp = service.users().messages().list(
            userId=user_id, q=q, pageToken=page_token, maxResults=batch_size
        ).execute()
        chunk = [m["id"] for m in resp.get("messages", [])]
        ids.extend(chunk)
        fetched += len(chunk)
        page_token = resp.get("nextPageToken")
        if not page_token or (max_results and fetched >= max_results):
            break
        # polite pacing
        time.sleep(0.2)
    return ids

def _fetch_messages(service, ids: Iterable[str]):
    user_id = "me"
    for mid in ids:
        m = service.users().messages().get(userId=user_id, id=mid, format="full").execute()
        headers = m["payload"].get("headers", [])
        subject = _get_header(headers, "Subject") or ""
        sender = _get_header(headers, "From") or ""
        date_hdr = _get_header(headers, "Date")
        date_dt = _parse_gmail_date(date_hdr)
        # if Gmail 'internalDate' exists, use it as a fallback
        if not date_dt and "internalDate" in m:
            date_dt = datetime.fromtimestamp(int(m["internalDate"]) / 1000, tz=timezone.utc)

        yield {
            "message_id": m["id"],
            "date": date_dt or datetime.now(timezone.utc),
            "title": subject,
            "sender": sender,
        }

# --------------------------------------------
# Main function you asked to finish
# --------------------------------------------
def get_email_list(
    service,
    db_url: str,
    start_date: Optional[str] = None,  # "YYYY-MM-DD"
    end_date: Optional[str] = None,    # "YYYY-MM-DD"
    max_results: Optional[int] = None  # limit total messages this run
):
    """
    - Ensures table exists
    - Figures out resume point from DB (max stored date) if start_date is None
    - Queries Gmail within [start_date, end_date] (inclusive by day)
    - Inserts (id, date, title, sender) with upsert (ignore duplicates)
    - Returns counts
    """
    engine = init_db(db_url)

    # Resolve date window
    utc_today = datetime.now(timezone.utc).date()
    default_start = datetime(utc_today.year - 1, utc_today.month, utc_today.day, tzinfo=timezone.utc)  # 1y back
    default_end = datetime(utc_today.year, utc_today.month, utc_today.day, tzinfo=timezone.utc)

    if start_date:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    else:
        start_dt = get_resume_start(engine, default_start)

    if end_date:
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    else:
        end_dt = default_end

    if end_dt < start_dt:
        raise ValueError("end_date must be on/after start_date")

    query = _gmail_query(start_dt, end_dt)

    ids = _list_message_ids(service, query, max_results or 0)
    inserted = 0
    batch = []
    BATCH_SIZE = 200

    for rec in _fetch_messages(service, ids):
        batch.append(rec)
        if len(batch) >= BATCH_SIZE:
            inserted += store_batch(engine, batch)
            batch.clear()

    if batch:
        inserted += store_batch(engine, batch)

    return {
        "queried_ids": len(ids),
        "inserted_rows": inserted,
        "start_used": start_dt.isoformat(),
        "end_used": end_dt.isoformat(),
    }
