"""FastMCP tools for the Campus Customs operations database.

The server reads the working database copy only. It does not invent or
approximate business facts; every returned value comes from SQLite.
"""

from pathlib import Path
import sqlite3
from typing import Any

from fastmcp import FastMCP


DATABASE = Path(__file__).resolve().parents[1] / "data" / "campus_customs_new.db"
mcp = FastMCP("Campus Customs Operations")


def fetch_all(sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    """Run a read-only query and return SQLite rows as dictionaries."""
    with sqlite3.connect(f"file:{DATABASE}?mode=ro", uri=True) as connection:
        connection.row_factory = sqlite3.Row
        return [dict(row) for row in connection.execute(sql, params)]


@mcp.tool
def get_customer_order_context(ticket_id: int = 101) -> dict[str, Any]:
    """Return ticket, stock, price, and reprint-invoice facts for a customer order."""
    rows = fetch_all(
        """
        SELECT t.id AS ticket_id, t.type, t.requester, t.subject, t.sku,
               t.size, t.qty AS requested_qty, t.status AS ticket_status,
               t.notes, i.name AS product_name, i.qty AS stock_qty,
               i.location, p.unit_cost, p.list_price,
               inv.id AS invoice_id, inv.amount AS invoice_amount,
               inv.due_date AS invoice_due_date, inv.status AS invoice_status,
               inv.description AS invoice_description,
               v.name AS vendor_name, v.specialty AS vendor_specialty,
               v.lead_days AS vendor_lead_days
        FROM tickets t
        LEFT JOIN inventory i ON i.sku = t.sku AND i.size = t.size
        LEFT JOIN pricing p ON p.sku = t.sku
        LEFT JOIN invoices inv ON inv.id = t.invoice_id
        LEFT JOIN vendors v ON v.id = inv.vendor_id
        WHERE t.id = ?
        """,
        (ticket_id,),
    )
    return {"ticket": rows[0] if rows else None}


@mcp.tool
def get_rent_notice_context(ticket_id: int = 102) -> dict[str, Any]:
    """Return the lease and current-date facts needed to handle the rent ticket."""
    rows = fetch_all(
        """
        SELECT t.id AS ticket_id, t.type, t.requester, t.subject,
               t.status AS ticket_status, t.notes, t.created_at,
               l.id AS lease_id, l.space_name, l.landlord, l.monthly_rent,
               l.next_due, l.notes AS lease_notes,
               d.date_today
        FROM tickets t
        LEFT JOIN leases l ON l.id = t.lease_id
        CROSS JOIN desk d
        WHERE t.id = ?
        """,
        (ticket_id,),
    )
    return {"ticket": rows[0] if rows else None}


@mcp.tool
def get_bulk_discount_context(ticket_id: int = 103) -> dict[str, Any]:
    """Return real bulk-request quantity, stock, cost, and list-price facts."""
    rows = fetch_all(
        """
        SELECT t.id AS ticket_id, t.type, t.requester, t.subject, t.sku,
               t.size, t.qty AS requested_qty, t.status AS ticket_status,
               t.notes, i.name AS product_name, i.qty AS stock_qty,
               i.location, p.unit_cost, p.list_price
        FROM tickets t
        LEFT JOIN inventory i ON i.sku = t.sku AND i.size = t.size
        LEFT JOIN pricing p ON p.sku = t.sku
        WHERE t.id = ?
        """,
        (ticket_id,),
    )
    return {"ticket": rows[0] if rows else None}


@mcp.tool
def list_open_tickets() -> dict[str, Any]:
    """List the current open work queue from the tickets table."""
    return {"tickets": fetch_all("SELECT * FROM tickets WHERE status = 'open' ORDER BY id")}


@mcp.tool
def get_cash_position() -> dict[str, Any]:
    """Return recorded cash balances and payment history for finance review."""
    return {
        "cash_accounts": fetch_all("SELECT * FROM cash_accounts ORDER BY name"),
        "payments": fetch_all("SELECT * FROM payments ORDER BY id"),
        "open_invoices": fetch_all("SELECT * FROM invoices WHERE status = 'open' ORDER BY due_date, id"),
    }


@mcp.tool
def get_vendor_context(vendor_id: int | None = None) -> dict[str, Any]:
    """Return vendor capabilities and lead times, optionally for one vendor."""
    if vendor_id is None:
        vendors = fetch_all("SELECT * FROM vendors ORDER BY id")
    else:
        vendors = fetch_all("SELECT * FROM vendors WHERE id = ?", (vendor_id,))
    return {"vendors": vendors}


if __name__ == "__main__":
    mcp.run()
