"""
server.py
---------
A lightweight web server that gives your NL-to-SQL agent a browser interface.

It does two things:
  1. Serves the dashboard HTML page when you open localhost:8000 in a browser
  2. Listens for questions from the dashboard, runs them through the agent,
     and sends the answers back

How to run:
  pip install fastapi uvicorn
  python3 server.py

Then open your browser and go to: http://localhost:8000
"""

import json
import os
from datetime import datetime

# FastAPI is a simple Python web framework — it lets your script
# receive and respond to requests from a browser
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Your existing agent and logger — nothing changes inside them
from agent import ask
from eval_logger import LOG_PATH

# ---------------------------------------------------------------------------
# Create the web application
# ---------------------------------------------------------------------------
app = FastAPI()

# CORS middleware lets the browser talk to the server freely on localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# This defines the shape of the data the browser sends when asking a question
# ---------------------------------------------------------------------------
class QuestionRequest(BaseModel):
    question: str   # just the question text

# ---------------------------------------------------------------------------
# ROUTE 1: Serve the dashboard
# When someone opens http://localhost:8000 this sends back the HTML page
# ---------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """Reads dashboard.html and sends it to the browser."""
    with open("dashboard.html", "r") as f:
        return f.read()

# ---------------------------------------------------------------------------
# ROUTE 2: Answer a question
# The browser sends a question here, this runs it through your LangGraph
# agent and sends the result back as JSON
# ---------------------------------------------------------------------------
@app.post("/ask")
async def answer_question(request: QuestionRequest):
    """
    Receives a question from the dashboard, runs it through the agent,
    returns the result as JSON so the dashboard can display it.
    """
    if not request.question.strip():
        return JSONResponse({"error": "Please enter a question."}, status_code=400)

    # This is the exact same ask() function from agent.py — nothing changes
    result = ask(request.question)

    return {
        "question":            result["question"],
        "sql_query":           result["sql_query"],
        "final_answer":        result["final_answer"],
        "hallucination_flags": result["hallucination_flags"],
        "sql_error":           result["sql_error"],
        "success":             result["sql_error"] is None,
    }

# ---------------------------------------------------------------------------
# ROUTE 3: Return eval metrics for the dashboard panel
# Reads the eval log and computes live stats
# ---------------------------------------------------------------------------
@app.get("/metrics")
async def get_metrics():
    """
    Reads logs/eval_log.jsonl and returns summary stats for the dashboard.
    Called automatically by the dashboard every time it loads.
    """
    if not os.path.exists(LOG_PATH):
        return {
            "total": 0, "success_rate": 0, "hallucination_rate": 0,
            "recent": [], "failures": []
        }

    entries = []
    with open(LOG_PATH, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))

    if not entries:
        return {
            "total": 0, "success_rate": 0, "hallucination_rate": 0,
            "recent": [], "failures": []
        }

    total          = len(entries)
    successes      = sum(1 for e in entries if e["success"])
    hallucinations = sum(1 for e in entries if e["had_hallucination"])

    # Last 5 queries for the recent activity panel
    recent = [
        {
            "question": e["question"],
            "success":  e["success"],
            "had_hallucination": e["had_hallucination"],
            "timestamp": e["timestamp"][:16].replace("T", " "),  # clean up format
        }
        for e in reversed(entries[-5:])
    ]

    # All failures for the failures panel
    failures = [
        {
            "question": e["question"],
            "sql":      e["sql_generated"],
            "error":    e["sql_error"],
        }
        for e in entries if not e["success"]
    ]

    return {
        "total":              total,
        "success_rate":       round(100 * successes / total),
        "hallucination_rate": round(100 * hallucinations / total),
        "recent":             recent,
        "failures":           failures[-3:],   # last 3 failures only
    }

# ---------------------------------------------------------------------------
# Start the server when you run: python3 server.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    print("\n  NL-to-SQL Dashboard running at: http://localhost:8000")
    print("  Open that URL in your browser.")
    print("  Press Ctrl+C to stop.\n")
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
