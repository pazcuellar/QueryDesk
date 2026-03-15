# NL-to-SQL Agent — Portfolio Project
### Built with LangGraph + Llama 3 8B (Ollama) + SQLite
### Runs 100% locally on your MacBook — no API key, no cost

This project converts natural language questions into SQL queries using a
LangGraph state machine — the same framework Uber uses to power their internal
AI agent (Genie). It includes a built-in eval framework that logs every query,
flags hallucinations, and produces a success/failure report.

The model choice (Llama 3 8B via Ollama) mirrors Uber's own strategy:
use open-source models for high-volume, cost-sensitive tasks. The eval
framework documents exactly where the smaller model struggles vs GPT-4 —
which is itself a valuable insight to bring to a technical interview.

---

## Project structure

```
nl_to_sql/
├── main.py                  ← Run this to demo the agent
├── agent.py                 ← The LangGraph agent (all the logic)
├── eval_logger.py           ← Records results + hallucination flags
├── data/
│   ├── generate_sample.py   ← Creates the NYC taxi SQLite database
│   └── nyc_taxi.db          ← Generated automatically on first run
└── logs/
    └── eval_log.jsonl       ← Every query logged here (auto-created)
```

---

## Setup

### 1. Install Ollama — runs Llama 3 locally, free, no API key

1. Download and install from **https://ollama.com** (Mac app, ~200MB)
2. Open Terminal and pull the Llama 3 8B model (one-time download, ~4.7GB):
```bash
ollama pull llama3
```
3. Ollama runs automatically in the background. Verify it worked:
```bash
ollama list   # should show: llama3
```

### 2. Install Python dependencies

```bash
pip install langgraph langchain-openai openai
```

### 3. Generate the sample database

```bash
python data/generate_sample.py
```

### 4. Run the demo

```bash
python main.py
```

This runs 13 test questions — easy, tricky, and deliberately bad ones — and
prints a full eval report at the end.

---

## How the agent works (LangGraph flow)

```
[START]
   │
   ▼
schema_loader      ← reads DB structure so Llama 3 knows the real column names
   │
   ▼
sql_generator      ← sends question + schema to Llama 3 via Ollama, gets SQL back
   │                  (also cleans up Llama's markdown formatting habits)
   ▼
sql_validator      ← checks for dangerous commands (DROP/DELETE) and
   │                  hallucinated column names BEFORE running
   │
   ├─ (blocked) ──────────────────────────────────┐
   │                                              ▼
   └─ (safe) ──► sql_runner    result_formatter ◄─┘
                    │                 │
                    └────────────────►│
                                      ▼
                                   [END]
```

---

## Why Llama 3 8B is interesting for this project

Using a smaller local model (vs GPT-4) surfaces real failure modes to document:

| Failure mode | What happens | How this project catches it |
|---|---|---|
| Column hallucination | Llama invents columns from the full NYC TLC dataset (`pickup_latitude`, `rate_code`) that exist in training data but not our DB | `sql_validator` pattern matching |
| Markdown wrapping | Llama wraps SQL in ` ```sql ``` ` blocks | `sql_generator` cleanup regex |
| Preamble text | "Here is the SQL query: SELECT..." | Stripped by regex before SELECT |
| Ambiguous questions | "longest trip" → interprets as distance sometimes, duration others | Logged in eval report |

These failure modes map directly to what Uber's QueryGPT team deals with at scale.
Documenting them — and showing you built guardrails — is the interview artifact.

---

## The eval framework

Every question is logged to `logs/eval_log.jsonl` with:
- Original question
- SQL Llama 3 generated
- Whether it succeeded or failed
- Any hallucination flags triggered
- Timestamp

To see the full report:
```bash
python eval_logger.py
```

---

## The Uber parallel — what to say in the interview

> "This is structurally identical to Uber's QueryGPT — natural language in, SQL
> out, running against a production data source. The difference is their GenAI
> Gateway routes between GPT-4 for complex queries and Llama 3 for high-volume
> ones to manage cost. I built the same cost tradeoff logic here — Llama 3 8B
> locally for speed and cost, with a validator layer to catch where the smaller
> model fails. The eval log is my iteration surface — I can see exactly which
> question types break and improve the system prompt to fix them."

---

## Extending this project (next steps)

**Add model routing** — use Llama 3 8B for simple COUNT queries, fall back to
a stronger model for complex multi-table joins (mirrors Uber's Llama 3 vs GPT-4 strategy)

**Add memory** — store conversation history so users can ask follow-ups
("now filter that to just Manhattan pickups")

**Add a web UI** — wrap in FastAPI + a simple HTML form so it's demo-able
in a browser during interviews

**Swap the dataset** — point at any SQLite or Postgres database to make this
a real internal tool
