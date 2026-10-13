# Campus Customs HW5

This repository contains the Campus Customs MCP server, FastAPI agent team, React dashboard, database copies, and grading evidence.

## Setup

1. Copy `.env.example` to `.env` and add your own Portkey key. Never commit `.env`.
2. Create a clean working database whenever needed:

   ```bash
   cp data/campus_customs.db data/campus_customs_new.db
   ```

## Run the system

Start the MCP server from the project root:

```bash
python mcp_server/mcp_server.py
```

Start the FastAPI backend in a second terminal:

```bash
cd backend
uvicorn main:app --reload --port 8015
```

Start the React board in a third terminal:

```bash
cd frontend
npm install
npm run dev
```

The board uses `http://localhost:8015` for the API. Before a full three-ticket run, reset the database with the API route `POST http://localhost:8015/api/reset`, or copy the original database over the working copy as shown above. Then run tickets 101, 102, and 103 from the board. Agents prepare recommendations; a human must approve any payment or purchase before cash changes or a ticket resolves.

See `output/harness.md` for the system design, tools, agents, safety rules, limits, and route list.
