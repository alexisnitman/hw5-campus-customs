"""FastAPI dashboard backend for the Campus Customs agent team."""

import asyncio
import json
import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from team import run_ticket


ROOT = Path(__file__).resolve().parents[1]
DATABASE = ROOT / "data" / "campus_customs_new.db"
ORIGINAL_DATABASE = ROOT / "data" / "campus_customs.db"
AUDIT_FILE = ROOT / "output" / "audit_trail.json"

app = FastAPI(title="Campus Customs Agent Team API")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5178", "http://127.0.0.1:5178"], allow_methods=["*"], allow_headers=["*"])


class ApprovalRequest(BaseModel):
    approved_by: str = Field(min_length=1, max_length=120)


def query(sql: str, params: tuple = ()) -> list[dict]:
    with sqlite3.connect(DATABASE) as connection:
        connection.row_factory = sqlite3.Row
        return [dict(row) for row in connection.execute(sql, params)]


def ticket_rows() -> list[dict]:
    return query("SELECT id, type, requester, subject, status, sku, size, qty, lease_id, invoice_id, notes, created_at FROM tickets ORDER BY id")


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "port": 8000}


@app.get("/api/tickets")
def tickets() -> dict:
    """Return all three tickets and their current open/resolved status."""
    return {"tickets": ticket_rows()}


@app.post("/api/tickets/{ticket_id}/run")
async def run_ticket_route(ticket_id: int) -> dict:
    """Run the targeted agent plan for one ticket and return its report."""
    if ticket_id not in {101, 102, 103}:
        raise HTTPException(status_code=404, detail="Ticket must be 101, 102, or 103")
    try:
        result = await run_ticket(ticket_id)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Agent run failed: {exc}") from exc
    return result.model_dump(mode="json")


@app.get("/api/events")
def events(limit: int = 100) -> dict:
    """Return recent append-only agent events for dashboard refreshes."""
    limit = max(1, min(limit, 500))
    if not AUDIT_FILE.exists():
        return {"events": []}
    records = []
    for line in AUDIT_FILE.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return {"events": records[-limit:]}


@app.get("/api/cash")
def cash() -> dict:
    rows = query("SELECT name, balance, date FROM cash_accounts WHERE name = 'checking'")
    if not rows:
        raise HTTPException(status_code=404, detail="Checking account not found")
    return rows[0]


@app.post("/api/tickets/{ticket_id}/approve")
def approve(ticket_id: int, request: ApprovalRequest) -> dict:
    """Apply a human-approved payment or purchase and update checking cash."""
    if ticket_id not in {101, 102, 103}:
        raise HTTPException(status_code=404, detail="Ticket must be 101, 102, or 103")
    with sqlite3.connect(DATABASE) as connection:
        connection.row_factory = sqlite3.Row
        ticket = connection.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
        if ticket is None:
            raise HTTPException(status_code=404, detail="Ticket not found")
        account = connection.execute("SELECT * FROM cash_accounts WHERE name = 'checking'").fetchone()
        if account is None:
            raise HTTPException(status_code=404, detail="Checking account not found")
        if ticket_id == 101:
            invoice = connection.execute("SELECT * FROM invoices WHERE id = ?", (ticket["invoice_id"],)).fetchone()
            if invoice is None or invoice["status"] != "open":
                raise HTTPException(status_code=409, detail="Ticket 101 has no open invoice to pay")
            amount, kind, ref_id = invoice["amount"], "invoice", invoice["id"]
        elif ticket_id == 102:
            lease = connection.execute("SELECT * FROM leases WHERE id = ?", (ticket["lease_id"],)).fetchone()
            if lease is None:
                raise HTTPException(status_code=409, detail="Ticket 102 has no linked lease")
            amount, kind, ref_id = lease["monthly_rent"], "rent", lease["id"]
        else:
            row = connection.execute("SELECT t.qty, i.unit_cost FROM tickets t JOIN pricing i ON i.sku=t.sku WHERE t.id = ?", (ticket_id,)).fetchone()
            if row is None:
                raise HTTPException(status_code=409, detail="Ticket 103 has no verified pricing")
            amount, kind, ref_id = row["qty"] * row["unit_cost"], "purchase", ticket_id
        new_balance = account["balance"] - amount
        now = datetime.now(timezone.utc).isoformat()
        connection.execute("UPDATE cash_accounts SET balance = ?, date = ? WHERE name = 'checking'", (new_balance, now[:10]))
        connection.execute("INSERT INTO payments (kind, ref_id, amount, account, paid_at, approved_by) VALUES (?, ?, ?, 'checking', ?, ?)", (kind, ref_id, amount, now, request.approved_by))
        if ticket_id == 101:
            connection.execute("UPDATE invoices SET status = 'paid' WHERE id = ?", (ref_id,))
        connection.execute("UPDATE tickets SET status = 'resolved' WHERE id = ?", (ticket_id,))
    return {"ticket_id": ticket_id, "kind": kind, "amount": amount, "approved_by": request.approved_by, "checking_balance": new_balance, "overdraft": new_balance < 0, "status": "resolved"}


@app.post("/api/reset")
def reset() -> dict:
    """Restore the working database from the untouched original database."""
    shutil.copy2(ORIGINAL_DATABASE, DATABASE)
    return {"status": "reset", "database": str(DATABASE.name), "tickets": ticket_rows()}
