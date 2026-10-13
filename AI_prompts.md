# HW5 AI Prompt Log

This file records the prompts used while completing Homework 5. Each problem section will be updated as work continues.

## Problem 2 — Database schema and open-ticket relationships

**Prompt typed:** “Open the data 5/campus_customs.db in the HW5 folder and look through every table and its fields. Copy the original file to data 5/campus_customs_new.db as we are going to update the new file later. Then study the three open tickets so you can see how they link to other tables. Start a file in output/harness.md. In that file for each table please list the fields and one short line on why that table matters for the agents.”

**What was lacking after the first prompt:** The request did not specify a particular table order or a reporting format, so the schema was documented table by table and the ticket links were summarized separately.

**Follow-up prompt (if needed):** None yet.

## Problem 3 — FastMCP database tools

**Prompt typed:** “Write an MCP Server in mcp_server/ using FastMCP that reads data 5/campus_customs_new.db. Create three clear database-backed tools, document which tables and open ticket each tool supports in output/harness.md, and add mcp_server/README.md. Do not connect or run it yet.”

**What was lacking after the first prompt:** The three tool workflows were not named in advance, so they were selected from the three open tickets and their database relationships.

**Follow-up prompt (if needed):** None yet.

## Problem 4 — Connect and smoke-test the MCP server

**Prompt typed:** “Add the MCP server to this project using a project-root .mcp.json, connect to it, test all three MCP tools, and save output/mcp_smoke.json with the prompt, tool name, and exact tool output from campus_customs_new.db.”

**What was lacking after the first prompt:** The MCP connection format and evidence structure had to be added around the existing FastMCP server.

**Follow-up prompt (if needed):** None yet.

## Problem 5 — PydanticAI agentic operations team

**Prompt typed:** “Build a connected PydanticAI team for Campus Customs with Boss, Inventory, Accounting, Facilities, and Customer Service. Give each role detailed prompts and models, use only gpt-6-luna through Portkey, add any needed MCP tools, keep shop facts behind MCP, append auditable loop records, and document agents, tools, tables, safety, and token limits.”

**What was lacking after the first prompt:** The team needed explicit role boundaries, a delegation workflow, additional queue/finance/vendor MCP tools, and a shared audit format.

**Follow-up prompt (if needed):** None yet.

## Problem 6 — Expected ticket delegation plan

**Prompt typed:** “Before wiring the backend, create output/desk_tickets.html with tabs for tickets 101–103 plus empty Cash and Reflection tabs. For each ticket, document who the Boss should call first, all targeted delegations, and the expected MCP tools, leaving an Actual section for after the agents run.”

**What was lacking after the first prompt:** The actual agent runs have not happened yet, so only expected plans can be recorded and the Actual areas must remain empty.

**Follow-up prompt (if needed):** None yet.

## Problem 7 — FastAPI operations dashboard backend

**Prompt typed:** “In backend/main.py, use FastAPI to expose ticket status, targeted ticket agent runs, recent agent events, human approval of payments or purchases, current checking balance, and database reset routes. Run it from backend with uvicorn main:app --reload --port 8000 and document every route in harness.md.”

**What was lacking after the first prompt:** The route contracts and approval rules had to be defined so only the human approval route changes cash.

**Follow-up prompt (if needed):** None yet.

## Problem 8 — React agent-team dashboard

**Prompt typed:** “Build a React + Vite + TypeScript frontend dashboard that calls the Problem 7 backend at http://localhost:8000, lists the tickets, runs a selected ticket’s team, shows agent activity and summaries, supports human approval, refreshes checking cash, and documents the look in output/design.md.”

**What was lacking after the first prompt:** The dashboard needed a visual hierarchy and clear status treatment so activity, resolution, and human financial approval were easy to distinguish.

**Follow-up prompt:** “This dashboard looks too cookie cutter. Make the color scheme black and beige, make the boxes bold with dramatic contrast, and use a structured font that pops.”

**What was lacking after the follow-up:** The first design used a softer Yale blue/sea-glass palette and rounded cards, which did not provide the distinctive high-contrast editorial feel requested.

**Follow-up prompt (if needed):** None yet.

## Problem 9 — Full ticket run and resolution evidence

**Prompt typed:** “Reset the working database, run all three ticket teams, fill the Actual sections in desk_tickets.html, reconcile cash, save resolved_tickets.json and resolved_board.html, append real audit events, and finish harness.md.”

**What was lacking after the first prompt:** The database had to be reset and the real team runs and human approvals had to occur before Actual results and cash could be documented.

**Follow-up prompt:** “Ticket 103 was marked resolved after the agent review even though no action was completed, and the team activity is difficult to understand. Only mark tickets resolved after the actual action, and make activity human-readable.”

**What was lacking after the follow-up:** The dashboard treated a finished review as a completed business action and displayed raw audit JSON instead of plain-language explanations.

**Follow-up prompt:** “Ticket 103 says it is ready for approval, but the approval button disappears when I select another ticket and come back. Keep each completed ticket's agent result and approval button available when switching tickets.”

**What was lacking after the follow-up:** The dashboard stored only the most recently selected ticket's result instead of retaining a separate result for each ticket.

**Follow-up prompt:** “When I manually approve Ticket 103, the checking balance is too low. Human approval should override that limit.”

**What was lacking after the follow-up:** The approval route treated the balance check as an absolute block instead of recording the human-approved overdraft.

**Follow-up prompt (if needed):** None yet.

## Problem 10 — Agent team reflection

**Prompt typed:** “Fill the Reflection tab in output/desk_tickets.html. Evaluate the agents on each ticket, compare Actual with Expected, explain when one agent would be simpler, give three problems this team can solve and three it cannot, and tie everything to the three tickets and Cash tab in simple language.”

**What was lacking after the first prompt:** The reflection needed the real run outcomes and final cash evidence rather than generic descriptions of agent teams.

**Follow-up prompt (if needed):** None yet.
