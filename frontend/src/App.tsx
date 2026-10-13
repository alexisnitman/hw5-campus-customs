import { useEffect, useMemo, useState } from "react";
import { Activity, CheckCircle2, CircleDollarSign, Clock3, Play, RefreshCw, ShieldCheck, Sparkles } from "lucide-react";

const API = "http://localhost:8015";
type Ticket = { id:number; type:string; requester:string; subject:string; status:string; sku?:string; size?:string; qty?:number; notes:string };
type Event = { time?:string; agent:string; event:string; tool_name?:string; args?:string; result?:string; stop_reason?:string };
type Report = { role:string; decision:string; evidence:string[]; risks:string[]; next_steps:string[]; needs_human_approval:boolean };
type RunResult = { boss_summary:string; reports:Report[]; stop_reason:string };

const tone: Record<number,string> = {101:"customer",102:"facilities",103:"finance"};
const roleCopy: Record<string,string> = {Boss:"sets the route",Inventory:"checks stock",Accounting:"protects cash",Facilities:"handles the space", "Customer Service":"writes the human reply"};

function readableEvent(event: Event): string {
  if (event.event === "mcp_call") return event.tool_name ? `Checked ${event.tool_name.replace(/_/g, " ")}.` : "Checked the operations records.";
  if (event.event === "delegation") return "Received a focused assignment from Boss.";
  if (event.event === "stop") return event.stop_reason === "completed" ? "Finished the review and sent the recommendation to Boss." : `Stopped: ${event.stop_reason || "review ended"}.`;
  if (event.event === "agent_result" && event.result) {
    try { const report = JSON.parse(event.result); return report.decision || "Shared a recommendation with the team."; } catch { return "Shared a recommendation with the team."; }
  }
  return "Updated the ticket review.";
}

function eventBelongsToTicket(event: Event, ticketId: number): boolean {
  return Boolean(event.args?.includes(`"ticket_id": ${ticketId}`) || event.args?.includes(`"ticket_id":${ticketId}`) || event.result?.includes(`"ticket_ids": [${ticketId}]`));
}

function App() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [selected, setSelected] = useState(101);
  const [cash, setCash] = useState<{balance:number;date:string}|null>(null);
  const [events, setEvents] = useState<Event[]>([]);
  const [runs, setRuns] = useState<Record<number, RunResult>>({});
  const [running, setRunning] = useState(false);
  const [error, setError] = useState("");
  const [approved, setApproved] = useState<number[]>([]);

  const selectedTicket = tickets.find(t => t.id === selected);
  const run = runs[selected];
  const selectedEvents = useMemo(() => events.filter(e => e.agent === "Boss" || (selected === 101 && ["Inventory","Customer Service","Accounting"].includes(e.agent)) || (selected === 102 && ["Facilities","Accounting"].includes(e.agent)) || (selected === 103 && ["Inventory","Accounting"].includes(e.agent))), [events, selected]);
  const reviewComplete = Boolean(run) || events.some(e => e.agent === "Boss" && ((e.event === "stop" && e.stop_reason === "completed") || e.event === "agent_result") && eventBelongsToTicket(e, selected));
  const tracker = [
    {label:"Ticket queued", done:selectedEvents.length > 0 || Boolean(run)},
    {label:"MCP facts gathered", done:selectedEvents.some(e => e.event === "mcp_call" && Boolean(e.result))},
    {label:"Specialists review", done:selectedEvents.some(e => e.event === "agent_result" && e.agent !== "Boss")},
    {label:"Boss decision", done:selectedEvents.some(e => e.event === "agent_result" && e.agent === "Boss") || reviewComplete},
    {label:"Ready for approval", done:reviewComplete}
  ];

  async function load() {
    try {
      const [t, c, e] = await Promise.all([fetch(`${API}/api/tickets`), fetch(`${API}/api/cash`), fetch(`${API}/api/events?limit=120`)]);
      if (!t.ok || !c.ok || !e.ok) throw new Error("The operations API did not respond.");
      setTickets((await t.json()).tickets); setCash(await c.json()); setEvents((await e.json()).events);
    } catch (err) { setError(err instanceof Error ? err.message : "Could not load the dashboard."); }
  }
  useEffect(() => { void load(); }, []);

  async function startRun() {
    setRunning(true); setError("");
    const timer = window.setInterval(() => { fetch(`${API}/api/events?limit=120`).then(r => r.json()).then(data => setEvents(data.events)).catch(() => undefined); }, 900);
    try {
      const response = await fetch(`${API}/api/tickets/${selected}/run`, { method:"POST" });
      if (!response.ok) throw new Error((await response.json()).detail || "The team could not run.");
      const result:RunResult = await response.json(); setRuns(current => ({...current, [selected]: result}));
      await load();
    } catch (err) { setError(err instanceof Error ? err.message : "The team run failed."); }
    finally { window.clearInterval(timer); setRunning(false); }
  }

  async function approve() {
    setError("");
    try {
      const response = await fetch(`${API}/api/tickets/${selected}/approve`, {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({approved_by:"Dashboard human approver"})});
      if (!response.ok) throw new Error((await response.json()).detail || "Approval failed.");
      setApproved(a => [...a, selected]); await load();
    } catch (err) { setError(err instanceof Error ? err.message : "Approval failed."); }
  }

  return <div className="app-shell">
    <header className="topbar"><div className="brand"><span className="brand-mark">CC</span><div><strong>Campus Customs</strong><small>operations intelligence</small></div></div><div className="live"><span className="pulse"/> LIVE DESK <span className="date">· 31 AUG 2026</span></div></header>
    <main>
      <section className="hero"><div><h1>Good decisions,<br/><em>with a human in the loop.</em></h1><p className="lede">A focused command center for the team behind every Campus Customs order, bill, and storefront detail.</p></div><div className="hero-orbit"><Sparkles size={18}/><span>AI TEAM<br/><b>READY TO ASSIST</b></span></div></section>
      <section className="metrics"><div><span>OPEN QUEUE</span><strong>{tickets.filter(t=>t.status === "open").length.toString().padStart(2,"0")}</strong><small>tickets awaiting attention</small></div><div><span>CHECKING</span><strong>{cash ? `$${cash.balance.toLocaleString()}` : "—"}</strong><small>verified account balance</small></div><div><span>TEAM SIGNAL</span><strong>{running ? "ACTIVE" : "READY"}</strong><small>{running ? "agents are collaborating" : "select a ticket to begin"}</small></div></section>
      <div className="workspace"><aside className="ticket-list"><div className="section-label">WORK QUEUE <span>{tickets.length}</span></div>{tickets.map(t => <button key={t.id} className={`ticket-card ${selected===t.id?"chosen":""}`} onClick={() => {setSelected(t.id); setError("");}}><div className="ticket-top"><span className={`ticket-dot ${t.status}`}/><span className="ticket-id">#{t.id}</span><span className={`tag ${tone[t.id]}`}>{t.type.replace("_"," ")}</span></div><h3>{t.subject}</h3><p>{t.requester}</p><div className="ticket-bottom"><span>{t.status === "resolved" ? "Resolved" : "Open"}</span>{t.status === "resolved" ? <CheckCircle2 size={15}/> : <Clock3 size={15}/>}</div></button>)}</aside>
        <section className="command"><div className="command-head"><div><p className="kicker">SELECTED TICKET</p><h2>#{selectedTicket?.id} <span>{selectedTicket?.subject}</span></h2><p className="subline">{selectedTicket?.requester} · {selectedTicket?.notes}</p></div><button className="refresh" onClick={() => void load()}><RefreshCw size={16}/> Refresh</button></div>
          <div className="runbar"><div className="run-status"><span className={`status-orb ${running?"spinning":""}`}>{running?<Activity size={19}/>:<ShieldCheck size={19}/>}</span><div><strong>{running ? "The team is reviewing this ticket" : reviewComplete ? "Agent review complete" : "Ready for review"}</strong><small>{running ? "Watching the live audit trail…" : "Facts are read through the Campus Customs MCP server."}</small></div></div><button className="run-button" disabled={running} onClick={() => void startRun()}><Play size={16} fill="currentColor"/>{running ? "Running…" : "Start agent team"}</button></div>
          <div className="pizza-tracker"><div className="pizza-heading"><small>{running ? "Fresh from the oven…" : run ? "Ready to serve" : "Waiting for a ticket run"}</small></div><div className="pizza-steps">{tracker.map((step,index) => <div className={`pizza-step ${step.done?"done":""} ${index < tracker.length-1 && tracker[index+1].done?"passed":""}`} key={step.label}><span className="pizza-dot">{step.done ? "✓" : index + 1}</span><span>{step.label}</span></div>)}</div></div>
          {error && <div className="error">{error}</div>}
          <div className="agent-stream"><div className="stream-heading"><span>TEAM ACTIVITY</span><small>{selectedEvents.length} events</small></div>{selectedEvents.length === 0 && !running ? <div className="empty"><Activity size={28}/><p>Nothing here yet.<br/><span>Start the team to see each role work.</span></p></div> : <div className="events">{selectedEvents.slice(-8).map((event,i) => <div className="event" key={`${event.time}-${i}`}><div className={`avatar ${event.agent.toLowerCase().replace(" ","-")}`}>{event.agent.split(" ").map(x=>x[0]).join("")}</div><div><strong>{event.agent}</strong><small>{event.event === "mcp_call" ? "looked up verified shop facts" : event.event === "agent_result" ? "made a recommendation" : roleCopy[event.agent] || event.event}</small><p>{readableEvent(event)}</p></div><time>{event.time ? new Date(event.time).toLocaleTimeString([], {hour:"2-digit",minute:"2-digit"}) : "now"}</time></div>)}</div>}</div>
          {run && <div className="review"><div className="review-head"><span>TEAM READOUT</span><b>#{selected}</b></div><p className="boss-summary">{run.boss_summary}</p><div className="reports">{run.reports.map(report => <article key={report.role}><div className="report-role"><span className={`avatar mini ${report.role.toLowerCase().replace(" ","-")}`}>{report.role.split(" ").map(x=>x[0]).join("")}</span><strong>{report.role}</strong>{report.needs_human_approval && <span className="approval-needed">approval needed</span>}</div><p>{report.decision}</p>{report.next_steps[0] && <small>Next: {report.next_steps[0]}</small>}</article>)}</div></div>}
          {reviewComplete && <div className="approval"><div><CircleDollarSign size={21}/><div><strong>Human approval required</strong><small>The team prepared this action. Only you can authorize the cash change.</small></div></div><button disabled={approved.includes(selected) || selectedTicket?.status === "resolved"} onClick={() => void approve()}>{approved.includes(selected) || selectedTicket?.status === "resolved" ? "Approved" : "Approve payment / purchase"}</button></div>}
        </section></div>
    </main>
    <footer><span>Campus Customs / internal desk</span><span>Evidence-led · human-approved · Yale blue</span></footer>
  </div>;
}
export default App;
