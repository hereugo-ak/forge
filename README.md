# HYPERION

**many minds. one reading.**

HYPERION is a multi-agent consulting intelligence system that produces
premium PDF reports from business questions. It is NOT a generic LLM
wrapper — it is a proprietary consulting model with 20 specialized
agents, dynamic workflow orchestration, and a 5-stage report pipeline.

## Quick Start

```bash
# Clone and install
git clone https://github.com/your-org/hyperion.git
cd hyperion
uv sync

# Configure API keys
cp .env.example .env
# Edit .env with your API keys

# Run a consultation (non-interactive)
hyperion consult "Should we enter the Tier-2 Indian SaaS market?"

# Or launch the TUI (interactive)
hyperion shell
```

## Architecture

HYPERION is built on 5 principles from ARCHITECTURE.md:

1. **Dynamic Workflows** — No two engagements look the same. The
   Engagement Director decomposes each question into a custom DAG
   of tasks with dependencies and model tier assignments.

2. **20 Specialized Agents** — Each agent has proprietary skills,
   assigned tools, and a specific model tier. No generic agents.
   No idle tools. No decorative skills.

3. **5-Stage Pipeline** — Engagement Director → Specialists (parallel)
   → Fact Checker → Synthesis Lead → Quality Gate → Presentation
   Designer → Data Visualizer → Render Engine → PDF

4. **Adaptive Replanning** — The Engagement Director monitors the
   AgentBus for escalations and can spawn new agents, reroute
   dependencies, or reallocate model tiers mid-engagement.

5. **Premium Output** — 300 DPI PDFs with embedded fonts, brand
   colors (warm palette, no blue/purple AI slop), Tufte-compliant
   charts, and Pillow-processed images.

## Agent Roster

| # | Agent | Role | Tier |
|---|---|---|---|
| 1 | Engagement Director | Orchestrate, plan, adapt | STRONG |
| 2 | Synthesis Lead | Reconcile, synthesize, recommend | DEEP |
| 3-14 | 12 Specialists | Market, Competitive, Financial, Risk, Tech, Ops, Regulatory, Sustainability, Consumer, M&A, Innovation, Strategy | STANDARD/STRONG |
| 15 | Research Librarian | Vault management, citations | STANDARD |
| 16 | Fact Checker | Claim verification, contradictions | FAST |
| 17 | Data Visualizer | Charts, Tufte principles | STANDARD |
| 18 | Quality Gate | 10-dimension rubric scoring | STRONG |
| 19 | Presentation Designer | Layout, images, Jinja2 | STRONG |
| 20 | Render Engine | WeasyPrint, Pillow, PDF assembly | STANDARD |

## LLM Providers

All 4 providers expose OpenAI-compatible APIs:

| Provider | Models | Tiers Served |
|---|---|---|
| Google AI Studio | Gemma 4, Gemini 3.x | MICRO, FAST, STANDARD, DEEP |
| NVIDIA NIM | Nemotron 70B | STRONG |
| Cerebras | GPT OSS 120B | FAST, STRONG |
| Groq | Llama 3.3, GPT OSS | MICRO, FAST, STANDARD |

## TUI Commands

| Command | Description |
|---|---|
| `/consult <question>` | Start a new engagement |
| `/providers` | Show LLM provider status |
| `/vault <query>` | Search the Obsidian vault |
| `/export <format>` | Export report (pdf, markdown, json) |
| `/resume <id>` | Resume a previous engagement |
| `/help` | Show available commands |
| `/clear` | Clear current engagement |

## Project Structure

```
hyperion/
├── hyperion/
│   ├── cli.py              # Typer CLI
│   ├── config.py           # Pydantic Settings
│   ├── orchestrator.py     # WorkflowEngine
│   ├── router/             # LLM routing layer
│   ├── agents/             # 20-agent system
│   ├── schemas/            # Pydantic models
│   ├── tools/              # 13 tool clients
│   ├── output/             # PDF/charts/images/markdown
│   └── tui/                # Textual TUI
├── vault/                  # Obsidian vault (Second Brain)
├── reports/                # Generated PDFs
├── assets/                 # Fonts, cached images
└── tests/                  # Test suite
```

## Configuration

All configuration is via environment variables with `HYPERION_` prefix.
See `.env.example` for the full list.

Key settings:
- `HYPERION_GOOGLE_API_KEY` — Google AI Studio API key
- `HYPERION_NVIDIA_API_KEY` — NVIDIA NIM API key
- `HYPERION_CEREBRAS_API_KEY` — Cerebras API key
- `HYPERION_GROQ_API_KEY` — Groq API key
- `HYPERION_SEARXNG_URL` — SearxNG URL (default: http://localhost:8888)
- `HYPERION_VAULT_PATH` — Obsidian vault path (default: ./vault)

## License

Proprietary. © HYPERION Consulting.
