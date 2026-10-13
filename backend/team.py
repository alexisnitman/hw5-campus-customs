import asyncio
import json
from pathlib import Path
from typing import Any

from pydantic_ai import Agent

from config import MODEL_NAME, model
from mcp_tools import call_mcp, compact
from models import AgentReport, AuditEntry, TeamRun


ROOT = Path(__file__).resolve().parents[1]
PROMPTS = ROOT / "backend" / "prompts"
AUDIT = ROOT / "output" / "audit_trail.json"
MAX_LOOP_STEPS = 12


def audit(loop: int, agent: str, event: str, *, tool_name: str | None = None, args: Any = "", result: Any = "", stop_reason: str | None = None) -> None:
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    entry = AuditEntry(loop=loop, agent=agent, event=event, tool_name=tool_name, args=compact(args), result=compact(result), stop_reason=stop_reason)
    with AUDIT.open("a", encoding="utf-8") as handle:
        handle.write(entry.model_dump_json() + "\n")


def role_agent(role: str) -> Agent:
    prompt = (PROMPTS / f"{role.lower().replace(' ', '_')}.md").read_text(encoding="utf-8")
    return Agent(model(), system_prompt=prompt, output_type=AgentReport)


async def mcp_step(loop: int, agent: str, tool_name: str, arguments: dict[str, Any] | None = None) -> Any:
    audit(loop, agent, "mcp_call", tool_name=tool_name, args=arguments or {})
    result = await call_mcp(tool_name, arguments)
    audit(loop, agent, "mcp_call", tool_name=tool_name, result=result)
    return result


async def run_role(role: str, task: str, facts: Any, ticket_ids: list[int], loop: int) -> AgentReport:
    audit(loop, role, "delegation", args={"task": task, "ticket_ids": ticket_ids})
    agent = role_agent(role)
    prompt = f"Task:\n{task}\n\nVerified MCP evidence (use only this evidence):\n{json.dumps(facts, default=str)}"
    result = await agent.run(prompt)
    report = result.output
    audit(loop, role, "agent_result", result=report.model_dump())
    return report


async def run_team(objective: str = "Review and route all open Campus Customs tickets.") -> TeamRun:
    """Run the bounded Boss delegation loop across all five specialists."""
    loop = 1
    audit(loop, "Boss", "delegation", args={"objective": objective})
    queue = await mcp_step(loop, "Boss", "list_open_tickets")
    loop += 1
    if loop > MAX_LOOP_STEPS:
        audit(loop, "Boss", "stop", stop_reason="loop_limit")
        return TeamRun(objective=objective, boss_summary="Stopped at the loop limit.", stop_reason="loop_limit")

    inventory_facts, accounting_facts, facilities_facts, service_facts = await asyncio.gather(
        mcp_step(loop, "Inventory", "get_bulk_discount_context", {"ticket_id": 103}),
        mcp_step(loop, "Accounting", "get_cash_position"),
        mcp_step(loop, "Facilities", "get_rent_notice_context", {"ticket_id": 102}),
        mcp_step(loop, "Customer Service", "get_customer_order_context", {"ticket_id": 101}),
    )
    reports = await asyncio.gather(
        run_role("Inventory", "Assess ticket 103's stock and whether the requested quantity can be fulfilled. Do not approve pricing.", inventory_facts, [103], loop + 1),
        run_role("Accounting", "Review cash, open invoices, and payment controls for the open queue. Flag money decisions requiring approval.", accounting_facts, [101, 102, 103], loop + 1),
        run_role("Facilities", "Assess the rent notice in ticket 102 against the lease and current business date. Recommend an escalation if needed.", facilities_facts, [102], loop + 1),
        run_role("Customer Service", "Prepare a truthful customer-facing handling plan for ticket 101, clearly addressing stock and reprint timing without promising an order.", service_facts, [101], loop + 1),
    )
    loop += 2
    boss = role_agent("Boss")
    final_prompt = f"Objective: {objective}\nOpen-ticket queue: {json.dumps(queue, default=str)}\nSpecialist reports:\n{json.dumps([r.model_dump() for r in reports], default=str)}\nSynthesize a concise, approval-aware action plan. Do not invent facts."
    boss_result = await boss.run(final_prompt)
    boss_report = boss_result.output
    audit(loop, "Boss", "agent_result", result=boss_report.model_dump())
    summary = boss_report.decision + " " + " ".join(boss_report.next_steps)
    audit(loop, "Boss", "stop", stop_reason="completed", result=summary)
    return TeamRun(objective=objective, boss_summary=summary, reports=list(reports) + [boss_report], stop_reason="completed")


async def run_ticket(ticket_id: int) -> TeamRun:
    """Run only the specialists and MCP calls relevant to one open ticket."""
    plans = {
        101: {
            "objective": "Resolve customer order ticket 101 without promising unavailable stock.",
            "first_tool": ("get_customer_order_context", {"ticket_id": 101}),
            "roles": [("Inventory", "Check the exact requested SKU and size, stock, location, and reprint context.", [101]), ("Customer Service", "Prepare truthful customer wording based on the verified availability.", [101]), ("Accounting", "Review the linked open reprint invoice and identify approval needs.", [101])],
        },
        102: {
            "objective": "Resolve rent notice ticket 102 with lease and payment controls.",
            "first_tool": ("get_rent_notice_context", {"ticket_id": 102}),
            "roles": [("Facilities", "Verify the lease, due date, landlord, and urgency.", [102]), ("Accounting", "Review current cash and payment records before any rent action.", [102])],
        },
        103: {
            "objective": "Review bulk hoodie discount ticket 103 without approving an unsupported offer.",
            "first_tool": ("get_bulk_discount_context", {"ticket_id": 103}),
            "roles": [("Inventory", "Compare requested quantity with verified size-M stock.", [103]), ("Accounting", "Review cost, list price, and cash/approval implications of a purchase or discount.", [103])],
        },
    }
    plan = plans.get(ticket_id)
    if not plan:
        raise ValueError(f"Unknown ticket ID: {ticket_id}")
    loop = 1
    audit(loop, "Boss", "delegation", args={"ticket_id": ticket_id, "objective": plan["objective"]})
    first_name, first_args = plan["first_tool"]
    facts = await mcp_step(loop, "Boss", first_name, first_args)
    if ticket_id in (102, 103):
        loop += 1
        extra = await mcp_step(loop, "Boss", "get_cash_position")
        facts = {"ticket": facts, "cash": extra}
    loop += 1
    reports = await asyncio.gather(*(run_role(role, task, facts, ids, loop) for role, task, ids in plan["roles"]))
    loop += 1
    boss = role_agent("Boss")
    final = await boss.run(f"Objective: {plan['objective']}\nVerified MCP evidence:\n{json.dumps(facts, default=str)}\nSpecialist reports:\n{json.dumps([r.model_dump() for r in reports], default=str)}\nGive an approval-aware recommendation; do not claim any payment or purchase occurred.")
    boss_report = final.output
    audit(loop, "Boss", "agent_result", result=boss_report.model_dump())
    audit(loop, "Boss", "stop", args={"ticket_id": ticket_id}, stop_reason="completed", result=boss_report.decision)
    return TeamRun(objective=plan["objective"], boss_summary=boss_report.decision, reports=list(reports) + [boss_report], stop_reason="completed")


if __name__ == "__main__":
    print(asyncio.run(run_team()).model_dump_json(indent=2))
