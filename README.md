# QueryDesk - A Reusable Natural Language to SQL Framework

Paz Cuéllar - [LinkedIn](https://www.linkedin.com/in/pazcuellar/) 

<aside>
💡

Ask your database questions in plain English. Built with LangGraph, Llama 3, and SQLite. Runs entirely on your laptop. **Free**.

</aside>

---

## **What this is**

Most data is locked inside databases that only speak SQL, but not every human speaks SQL.

<img width="1918" height="956" alt="Screenshot 2026-03-15 at 2 04 22 a m" src="https://github.com/user-attachments/assets/9874f4e5-5bb1-4b8d-85bf-266329ba9f6d" />


Learning SQL is one of the skills that has shaped my career most. I have used it to find answers the team needed, and I have helped others build that skill too. But looking back, what SQL really taught me was not syntax. It taught me to ask questions of data, **that habit of questioning data has helped me reduce costs**, eliminate repetitive tasks, and find root causes that would have stayed invisible otherwise.

But it also made me a bottleneck.

I remember a marketing team I worked with closely. Commercial operations were moving fast — we were constantly drowning — and a significant part of that drowning was me acting as a translator between a database and a team that would have been able to answer their own questions far better than I could, if only they had not needed me in the middle. They knew the business. They knew what they were looking for. They just could not speak SQL. Not a lack of intelligence or curiosity on the business side — a lack of access.

Then I learned about [QueryGPT](https://query-gpt.com/?lang=es) and how they are already closing this gap. 

Inspired, I started working on QueryDesk, I wanted to understand the natural language to SQL framework - you ask a question in plain English, it figures out the SQL, validates it for safety, runs it, and gives you the answer. No SQL knowledge required. No translator needed.

---

## QueryDesk Running

Run the project, open [localhost](http://localhost:8000) on your browser and you can choose an static question example or ask your own, you’ll get back the numeric answer and the sql query

<img width="1273" height="675" alt="Screenshot 2026-03-15 at 12 56 14 p m" src="https://github.com/user-attachments/assets/a6816796-9ab1-4cbc-aeec-b90162c388b1" />


<img width="1593" height="954" alt="Screenshot 2026-03-15 at 12 26 06 a m" src="https://github.com/user-attachments/assets/5071af44-e8b4-4b72-b70d-eba97a95af4c" />


## **How the pipeline works — and why it's built this way? LanGraph**

Every question travels through five stations in order. Each station does one thing and passes the result, LanGraph connects those stations.

Through experimentation I noticed that giving a Gemini Gem structured phases — one phase to specialize, one to process, one to control the output — produced dramatically better results than asking for everything at once. 

LangGraph feels like the same intuition formalized into actual code. Instead of writing phases in a prompt and hoping the model follows them, you define stations in a framework that guarantees execution order, carries shared state between steps, and handles branching logic when decisions need to be made. 

**Station 1 — Schema Loader** Opens the database and reads the column names before the AI sees anything. This map gets sent to the model with every question so it never has to guess what columns exist. **Responsible for 0% column hallucination rate in testing.**

**Station 2 — SQL Generator** Combines your question with the database map and sends both to Llama 3. The model reads a system prompt — an instruction manual you control — and returns a SQL query. No explanation, no formatting, just the query. (using Few Shot Prompting like they did in the [early days of QueryGPT](https://www.uber.com/mx/en/blog/query-gpt/) that could evolve into RAG)

**Station 3 — SQL Validator** Scans the SQL before it touches the database. Blocks dangerous commands (DROP, DELETE, UPDATE, INSERT). Flags column names that don't exist in the schema. If blocked, the query never reaches the database.

**Station 4 — SQL Runner** The only station that opens the real database. Runs the validated SQL, captures the rows, captures any errors.

**Station 5 — Result Formatter**  Formats raw rows into readable answers. Writes a full record of the interaction — question, SQL, result, flags, timestamp — to the audit log before finishing. Records what broke so we can fix it. 

<aside>
💡

What excites me about where this goes next is that having a real framework unlocks the next layer: fine-tuning - thus a more powerful tool. 

</aside>

---

## **The eval framework - from audit trail to intelligence layer**

Most demos prove a system works. This one measures how well it works, documents where it fails, and points toward how it gets better.

As seen above, when each question runs through the pipeline gets logged automatically to `logs/eval_log.jsonl`  where each entry includes the SQL generated, whether it succeeded or failed, any hallucination flags, and a timestamp.  

That log is not just an audit trail. It is a learning surface.

To see a full report at any time:

```jsx
python3 eval_logger.py
```

The report shows:

- Total questions run
- Success rate
- Hallucination flag rate
- Every failure with its exact error
- Every hallucination with the specific flag triggered

<aside>
💡

That’s the panel you see on the right side of the interface. 

**Note**: After running python3 `main.py` in Terminal, refresh the browser and the metrics update immediately.

</aside>

---

**How I used it to improve the semantic layer**

After the first test run the log showed 83% success and two failures. Opening the log revealed both entries side by side, with the question, the SQL containing EXTRACT(), and the error `near FROM: syntax error`. The pattern was immediate. Same error message, same SQL function, two different questions. One root cause.

Without the log you would have seen two failures and a crash message in the terminal. With the log you saw the exact SQL that caused each crash. Knowing exactly what the model generated, what the database rejected, and that the hallucination validator found nothing suspicious - that eliminates every other possible cause and points directly to the fix.

The fix was not switching models. It was adding four lines to the instruction manual telling Llama 3 explicitly which SQLite syntax to use for time calculations. Fix applied. Log re-read. 100%.

<aside>
💡

That loop — automatic logging, pattern recognition, targeted fix, verified improvement — is the eval framework working exactly as intended. Not a record of what happened. A diagnostic tool for making it better.

</aside>

---

**Where this points next — model routing and the GenAI Gateway**

The log contains something else that becomes valuable at scale - a growing library of questions categorized by complexity, query type, and failure rate.

If I were to connect this framework to Hugging Face and a GenAI Gateway, the eval log is the dataset that trains the routing decision. You would take the accumulated query history, label each entry by complexity class, and use that labeled data to train a small fast classifier — the traffic director sitting at the front of the GenAI Gateway. Every incoming question gets classified first. Simple queries route to a fine-tuned Llama 3 8B running locally — fast, free, private. Complex queries route to a stronger model. Ambiguous queries route to a quality checking agent before the answer surfaces.

---

## **What you’ll find in the repo**

<aside>
💡

[QueryDesk - GitHub Repo](https://github.com/pazcuellar/QueryDesk/tree/main) 

</aside>

nl_to_sql/

├── agent.py               ← the pipeline — all intelligence lives here

├── eval_logger.py         ← records every query, generates reports

├── server.py              ← web server connecting browser to pipeline

├── dashboard.html         ← the browser interface

├── main.py                ← batch test runner

└── generate_sample.py ← creates the NYC taxi sample database

---

## **How to run it on your machine**

**Step 1 — install Ollama** Download from ollama.com. Then in Terminal:

```jsx
ollama pull llama3
```

This downloads Llama 3 once (~4.7GB). No API key needed. Everything runs locally.

**Step 2 — install Python dependencies**

```jsx
pip install langgraph langchain-openai openai fastapi uvicorn
```

**Step 3 — create the sample database**

```jsx
cd nl_to_sql
```

```jsx
python3 -c "exec(open('data/generate_sample.py').read())"
```

**Step 4 — run the batch test**

```jsx
python3 main.py
```

This runs 13 pre-written test questions and prints an eval report showing success rate, failures, and hallucination flags.

**Step 5 — open the dashboard**

```jsx
python3 server.py
```

Then open your browser and go to `http://localhost:8000.` Ask any question in plain English.

---

## **Bring Your Own Data**

The framework becomes yours with four changes.

**Change 1 — replace the database** Write a new version of `generate_sample.py` that creates your table and columns. Run it once. A new `.db` file is created.

**Change 2 — update the file path** In `agent.py` find the two lines that reference `data/nyc_taxi.db` — one in the schema loader, one in the SQL runner. Change both to your new filename.

**Change 3 — update the system prompt** In `agent.py` find the system_prompt variable inside `sql_generator`. Change the context sentence at the top to describe your data. Add any domain-specific rules — value formats, terminology, column relationships your data has that Llama might not infer correctly on its own.

**Change 4 — update the hallucination patterns** In `agent.py` find the HALLUCINATION_PATTERNS list. Remove the NYC taxi specific column names. Add columns that Llama might invent for your domain — run a few test questions first, see what it hallucinates, add those to the list.

**Change 5 — update the example chips** In `dashboard.html` find the EXAMPLES array in the JavaScript section. Replace the example questions with ones that make sense for your data.

That is everything. The pipeline, the validator structure, the eval logger, the server, and the dashboard carry over untouched.

### **Zoom into Change 3 & 4 - The system prompt is the main control surface**

If the model gets something wrong, the fix is almost always in the system prompt (Change 3 mentioned above, it happens during Station 2) not in the code, not in the model choice. The system prompt in `agent.py` is heavily commented to explain why each rule exists and what failure it was added to prevent. Reading it tells you the full history of what broke and how it was fixed.

When you adapt this to a new dataset, the system prompt is where most of your configuration work happens. Treat it like documentation — write rules that explain themselves.

---

## **What this framework does not do yet**

Being honest about limitations is more useful than hiding them.

- It does not route between models based on query complexity. Every question goes to Llama 3 8B regardless of difficulty. A production version would send simple COUNT queries to the small model and escalate complex joins to a stronger one.
- It does not cache results. Identical questions hit the model every time.
- It does not have a feedback mechanism. There is no way for a user to mark an answer as wrong and have that feed back into prompt improvement automatically.
- It does not support multi-turn conversation. Each question is independent — you cannot ask "now filter that to just Manhattan" as a follow-up.
- It uses SQLite only. A production version would connect to Postgres, BigQuery, or Snowflake.
- It does not include authenticated login

These are the next steps for anyone who wants to extend it.

---

## **Why Llama 3 running locally**

### It’s Free

But also, privacy. No question you ask ever leaves your machine. For internal business data this matters — you are not sending company data to an external API.

---

## **Continuous Improvement**

What I am most proud of is not the query generation itself — it is the layer around it.

 The system validates every query before it touches real data, blocking anything dangerous. It logs every interaction with hallucination flags and error types. It measures its own accuracy and documents where it fails. When it failed — and it did fail — I identified the exact pattern, fixed it through a targeted prompt update, and verified the improvement. That loop is the part that scales.

The framework is not tied to any specific dataset. The NYC taxi data included in the repository is the proving ground. Your dataset — your team's data, your company's questions — is the next one. Adapting it requires five configuration changes. Everything else carries over.

If you are working on something similar, thinking about natural language interfaces for internal data, or just have a thought on what breaks in systems like this at scale — I would genuinely love to hear it.

The full write-up, including the architecture, the eval results, and the failure documentation, is in the link below.
