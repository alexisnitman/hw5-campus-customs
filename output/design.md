# Campus Customs dashboard design

## What I chose

- **Command-center layout:** A compact work queue sits beside the selected-ticket workspace, so a manager can move from ticket 101, 102, or 103 without losing context.
- **Distinct ticket signals:** Each ticket has a colored category tag for customer, facilities, or finance work, plus open/resolved dots and status text. This makes the queue scannable before reading details.
- **Agent activity stream:** Live audit events appear as role avatars with short descriptions of what each agent did and which MCP tool it used. Each role has a different color and one-line specialty, so the team feels like a set of recognizable colleagues rather than one anonymous chatbot.
- **Team readout cards:** After a run, the Boss summary appears above one card per participating agent. Each card shows the decision and next step, while an “approval needed” marker makes human responsibility visible.
- **Human-in-the-loop approval:** Cash-changing actions are separated in an amber approval panel. The dashboard explains that agents only prepare the action; the human button calls the approval route and the balance refreshes afterward.
- **Financial visibility:** Checking balance is a prominent metric at the top. It is fetched from the database and visibly refreshes after an approved payment or purchase.

## Creative choices and why they help

The visual style combines Yale blue, quiet sea-glass green, warm amber approval accents, and editorial serif headlines. The large italic headline, circular “team ready” mark, soft paper-like background, and rounded cards give the internal tool a boutique Campus Customs identity instead of making it feel like a generic admin table. The calm palette keeps financial decisions serious, while the small motion on the active status orb gives the board a sense of live collaboration.

The interface uses plain-language labels such as “Ready for review,” “Team activity,” and “Human approval required.” This helps a manager understand what is happening without reading model terminology. The dashboard calls `http://localhost:8015` in this local setup, refreshes the event trail during a run, and keeps the queue visible even when a specialist is working.

## Visual revision

The dashboard now uses a black-and-beige editorial system with rust, muted gold, and plum role accents. Heavy black borders, square corners, offset shadows, and strong light/dark blocks make the board feel distinctive instead of like a generic admin template. Structured mono labels and bold uppercase sans-serif headlines make ticket IDs, statuses, and decisions pop while keeping explanatory text readable.
