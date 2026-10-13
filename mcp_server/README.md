# Campus Customs MCP server

This FastMCP server gives future Campus Customs agents safe, focused tools for reading operational facts. It uses read-only SQLite queries and returns only values present in:

```text
data/campus_customs_new.db
```

The current tools are:

- `get_customer_order_context`: joins ticket 101 to its requested SKU/size in `inventory` and `pricing`, plus its reprint `invoices` and `vendors` records.
- `get_rent_notice_context`: joins ticket 102 to its `leases` record and the current date in `desk`.
- `get_bulk_discount_context`: joins ticket 103 to its requested SKU/size in `inventory` and `pricing` for a stock and discount review.
- `list_open_tickets`: reads the open work queue from `tickets` so the Boss can route work.
- `get_cash_position`: reads `cash_accounts`, `payments`, and open `invoices` for Accounting's cash and payment review.
- `get_vendor_context`: reads `vendors` for supplier specialty and lead-time checks.

The complete tool list is therefore: `get_customer_order_context`, `get_rent_notice_context`, `get_bulk_discount_context`, `list_open_tickets`, `get_cash_position`, and `get_vendor_context`.

More tools can be added later as new agent workflows require them. The server was connected and smoke-tested in Problem 4; the evidence is saved in `output/mcp_smoke.json`.

## Local connection

The project-root `.mcp.json` registers this server as `campus_customs` and starts it with the HW5 virtual environment. The server uses the stdio transport, so an MCP-capable client starts it on demand rather than requiring a separately running web server.
