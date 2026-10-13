from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field


class AgentReport(BaseModel):
    role: str
    ticket_ids: list[int] = Field(default_factory=list)
    decision: str
    evidence: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)
    needs_human_approval: bool = False


class TeamRun(BaseModel):
    objective: str
    boss_summary: str
    reports: list[AgentReport] = Field(default_factory=list)
    stop_reason: str


class AuditEntry(BaseModel):
    time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    loop: int
    agent: str
    event: Literal["delegation", "mcp_call", "agent_result", "stop"]
    tool_name: str | None = None
    args: str = ""
    result: str = ""
    stop_reason: str | None = None


class MCPCall(BaseModel):
    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
