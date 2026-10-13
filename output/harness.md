# Campus Customs HW5 database harness

The original database is `data 5/campus_customs.db`. A working copy was created at `data 5/campus_customs_new.db`; later changes should be made to the new copy so the original remains available for comparison.

## Tables and fields

### `cash_accounts`

| Field | Why it matters to agents |
|---|---|
| `name` | Identifies the cash account, such as checking. |
| `balance` | Shows available cash for payment and business decisions. |
| `date` | Indicates when the balance was recorded. |

This table helps an agent assess whether the shop has enough cash for a payment.

### `desk`

| Field | Why it matters to agents |
|---|---|
| `date_today` | Provides the business date for due-date and urgency calculations. |
| `notes` | Holds current operating notes for agent context. |

This table is the shop's small current-state context and helps agents interpret dates.

### `inventory`

| Field | Why it matters to agents |
|---|---|
| `sku` | Connects stock to a specific product and to pricing or tickets. |
| `name` | Gives the agent a readable product name. |
| `size` | Identifies the requested size or one-size option. |
| `qty` | Shows the real quantity available for an SKU and size. |
| `location` | Tells staff where to find or pick the item. |

This table is the source of truth for stock, fulfillment, and customer-order questions.

### `invoices`

| Field | Why it matters to agents |
|---|---|
| `id` | Identifies an invoice and links it to tickets or payments. |
| `vendor_id` | Connects the bill to the vendor that should be paid. |
| `amount` | States the exact amount owed. |
| `due_date` | Supports payment scheduling and overdue warnings. |
| `status` | Shows whether the invoice is open or already handled. |
| `description` | Explains what the invoice is for. |

This table lets agents triage bills and connect a ticket to a specific payable.

### `leases`

| Field | Why it matters to agents |
|---|---|
| `id` | Identifies a lease referenced by a ticket. |
| `space_name` | Identifies the rented shop location. |
| `landlord` | Names the party receiving rent. |
| `monthly_rent` | Gives the recurring rent amount. |
| `next_due` | Supports reminders and urgency decisions. |
| `notes` | Stores lease-specific details. |

This table gives agents the facts needed to handle rent notices and occupancy costs.

### `payments`

| Field | Why it matters to agents |
|---|---|
| `id` | Identifies a recorded payment. |
| `kind` | Describes what the payment was for. |
| `ref_id` | Links the payment to an invoice or other record when applicable. |
| `amount` | Records how much was paid. |
| `account` | Shows which cash account funded it. |
| `paid_at` | Records when the payment happened. |
| `approved_by` | Provides an accountability trail for approval. |

This table prevents agents from treating an unpaid invoice as paid and supports auditability.

### `pricing`

| Field | Why it matters to agents |
|---|---|
| `sku` | Links prices to the exact inventory product. |
| `unit_cost` | Shows the shop's cost and supports margin calculations. |
| `list_price` | Shows the normal customer-facing price. |

This table lets agents answer price questions and evaluate discounts without guessing.

### `tickets`

| Field | Why it matters to agents |
|---|---|
| `id` | Identifies and tracks a support or operations request. |
| `type` | Tells the agent what workflow applies, such as order, rent, or price override. |
| `requester` | Identifies who needs a response. |
| `subject` | Provides the short issue title. |
| `sku` | Links product-related tickets to inventory and pricing. |
| `size` | Captures the requested product size. |
| `qty` | Captures the requested quantity. |
| `lease_id` | Links rent tickets to lease facts. |
| `invoice_id` | Links payment tickets to invoice facts. |
| `status` | Shows whether the ticket still needs work. |
| `notes` | Contains the request's operational details. |
| `created_at` | Establishes ticket age and ordering. |

This is the agent's work queue: it brings together customer, inventory, rent, and finance tasks.

### `vendors`

| Field | Why it matters to agents |
|---|---|
| `id` | Identifies a vendor referenced by invoices. |
| `name` | Gives the agent the vendor's readable name. |
| `specialty` | Shows what the vendor supplies or does. |
| `lead_days` | Helps estimate how long a reorder or service may take. |

This table supports vendor selection, invoice explanations, and realistic timing.

## Open-ticket relationships

The database has three open tickets:

1. Ticket `101` is a customer order for one `CC-TEE-WHITE` in size S. It links to `inventory` and `pricing`: stock is `0`, list price is `$28.00`, and the item is in Aisle B. It has no lease or invoice link.
2. Ticket `102` is a rent notice from Elm City Properties. Its `lease_id` is `1`, linking to the Chapel Street shop lease with `$2,400` monthly rent due on `2026-09-02`. It has no invoice link.
3. Ticket `103` is a bulk price-override request from Yale AI Club for 20 `CC-HOOD-NAVY` hoodies in size M. It links to `inventory` and `pricing`: there are 8 in stock, unit cost is `$22`, and list price is `$58`. It has no lease or invoice link.

Ticket `101` also shows why relationships matter: the requested size is out of stock, while invoice `501` separately records an open `$840` rush reprint for that SKU and size. Invoice `501` links through `vendor_id=1` to Bulldog Print Co, whose specialty is apparel reprints and whose lead time is 5 days. Agents should follow foreign-key fields and verify current quantities and financial status before making commitments.

## Problem 3: MCP tools

The FastMCP server is in `mcp_server/mcp_server.py` and reads only `data 5/campus_customs_new.db`. It uses read-only SQLite queries, so agents receive database facts without fabricated values.

| MCP tool | Tables read | Ticket it helps unlock | Why it is the right tool |
|---|---|---|---|
| `get_customer_order_context` | `tickets`, `inventory`, `pricing`, `invoices`, `vendors` | `101` | Ticket 101 asks for one Bulldog Tee in size S, so this join checks the exact size's stock and price and also exposes the linked reprint invoice/vendor context. |
| `get_rent_notice_context` | `tickets`, `leases`, `desk` | `102` | Ticket 102 is a rent notice, so this tool connects the request to the Chapel Street lease and the database's current business date for due-date handling. |
| `get_bulk_discount_context` | `tickets`, `inventory`, `pricing` | `103` | Ticket 103 requests 20 navy hoodies in size M, so this tool compares the requested quantity with real stock and provides cost/list-price facts for a discount review. |

The server is intentionally not started for Problem 3, as requested.

## Problem 5: agentic operations team

The team is implemented in `backend/team.py`. Every role is a PydanticAI `Agent` using the same Portkey model, `gpt-6-luna`; no other model is configured. Each role has its own detailed system prompt in `backend/prompts/`. `backend/config.py` loads `PORTKEY_API_KEY` from the project `.env` and creates the OpenAI-compatible Portkey model. `backend/mcp_tools.py` is only an MCP client bridge: it launches/calls `mcp_server/mcp_server.py`, so the team does not create a second direct SQLite shop-tools layer.

### Roles

| Agent | Scope and responsibility |
|---|---|
| Boss | Reads the open queue, delegates work, reconciles reports, prioritizes, and marks human approvals; it does not approve money or customer exceptions itself. |
| Inventory | Checks SKU/size quantities, fulfillment capacity, locations, reprints, and stock shortfalls. |
| Accounting | Reviews cash, payments, invoices, costs, prices, margin concerns, and approval controls. |
| Facilities | Handles leases, rent notices, premises, business dates, and landlord escalation. |
| Customer Service | Creates truthful, privacy-aware customer wording and avoids promises unsupported by evidence. |

The bounded workflow first asks MCP for the open queue, gathers specialist evidence concurrently, delegates one task to each specialist, and then asks Boss to synthesize the reports. Reports use `AgentReport` with role, ticket IDs, decision, evidence, risks, next steps, and a human-approval flag. The final `TeamRun` contains the objective, Boss summary, reports, and stop reason.

### MCP tools available to the team

| MCP tool | Tables read | Team users |
|---|---|---|
| `get_customer_order_context` | `tickets`, `inventory`, `pricing`, `invoices`, `vendors` | Customer Service, Inventory, Accounting for ticket 101's size stock, price, reprint invoice, and vendor lead time. |
| `get_rent_notice_context` | `tickets`, `leases`, `desk` | Facilities and Accounting for ticket 102's lease, due date, landlord, and current business date. |
| `get_bulk_discount_context` | `tickets`, `inventory`, `pricing` | Inventory and Accounting for ticket 103's requested quantity, size-M stock, cost, and list price. |
| `list_open_tickets` | `tickets` | Boss uses it to discover and route the current open queue. |
| `get_cash_position` | `cash_accounts`, `payments`, `invoices` | Accounting uses it to review recorded cash, payment history, and open payables. |
| `get_vendor_context` | `vendors` | Inventory and Accounting use it to compare verified vendor specialties and lead times. |

### Audit, safety, and limits

Each delegation, MCP call/result, agent result, and final stop is appended as one JSON object per line to `output/audit_trail.json`. The `AuditEntry` fields are time, loop, agent, event, tool name, short arguments, short result, and stop reason. The file is opened with append mode and is never wiped between runs.

Real-business guardrails are built into the prompts: agents must use MCP evidence rather than guesses; must protect customer, vendor, cash, and credential information; must not reveal internal costs or balances to customers; must not make payments, alter records, approve discounts, promise inventory or delivery, or claim an order is complete; and must escalate money, exceptions, missing evidence, and conflicting records to a human. Customer Service keeps internal finance and vendor details out of customer messages.

The team has a maximum of 12 audited loop steps, one bounded specialist pass, and one Boss synthesis pass. MCP results are compacted to 1,800 characters in audit records, recent prompts are task-specific, and specialist evidence is fetched only for the relevant open-ticket workflows. These limits control token use while preserving a trace of every decision.

## Problem 7: FastAPI dashboard routes

Start from `backend/` with `uvicorn main:app --reload --port 8015`; the dashboard base URL is `http://localhost:8015`.

- `GET /api/health` — confirms the backend is running on port 8015.
- `GET /api/tickets` — returns tickets 101, 102, and 103 with their current fields and open/resolved status.
- `POST /api/tickets/{ticket_id}/run` — runs the targeted agent plan for ticket 101, 102, or 103 and returns the structured team result.
- `GET /api/events?limit=100` — returns recent append-only agent-loop events, including agent results, MCP tool names, and arguments/results for dashboard refreshes.
- `GET /api/cash` — returns the current checking balance from `cash_accounts`.
- `POST /api/tickets/{ticket_id}/approve` — applies a human-approved invoice, rent payment, or purchase, inserts a payment, deducts checking cash, and resolves the ticket. Because this endpoint represents an explicit human override, it permits an overdraft and returns `overdraft: true` when the resulting balance is negative.
- `POST /api/reset` — copies the untouched original database over `campus_customs_new.db` so a fresh run can begin.

## Problem 9: final ticket run and cash reconciliation

The working database was reset before the fresh run, producing a starting checking balance of `$3,400.00`. The team then ran ticket 101, ticket 102, and ticket 103. Alexis Nitman approved only the invoice for `$840.00` and rent for `$2,400.00`, leaving `$160.00`. Ticket 103 requested 20 medium hoodies while only 8 were in stock; the agents prepared a potential `$440.00` purchase recommendation but could not approve it or resolve the ticket. The ending balance is `$160.00` (`$3,400 - $840 - $2,400`), matching `cash_accounts.balance` in the working database. `output/audit_trail.json` contains the appended real run events, and the ticket evidence files show that 103 remains open until a human approves it.
