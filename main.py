"""
main.py
-------
Entry point for the NL-to-SQL LangGraph demo.

Run this file to:
  1. Ask a set of pre-written test questions (good, tricky, and bad ones)
  2. See the SQL Llama 3 generated for each
  3. See the results (or errors)
  4. Print the eval report showing success rate + hallucinations

Usage:
  python main.py

Requirements:
  pip install langgraph langchain-openai openai

"""

import os
from agent       import ask
from eval_logger import print_eval_report

# ---------------------------------------------------------------------------
# SEPARATOR — just a visual helper for the console output
# ---------------------------------------------------------------------------
def divider(char="-", width=60):
    print(char * width)


# ---------------------------------------------------------------------------
# TEST QUESTIONS
# These are designed to test different scenarios:
#   - Easy questions that should work perfectly
#   - Medium questions that need aggregation or filtering
#   - Tricky questions that might cause hallucinations
#   - Bad questions that ask for data that doesn't exist
# ---------------------------------------------------------------------------
TEST_QUESTIONS = [

    # ---- EASY: should work cleanly ----------------------------------------
    "How many trips are in the database?",
    "What are the different payment types used?",
    "Show me the 5 most expensive trips by total amount.",

    # ---- MEDIUM: needs aggregation ----------------------------------------
    "What is the average fare amount?",
    "Which vendor had the most trips?",
    "How many trips were paid by credit card vs cash?",
    "What is the average tip amount for each borough pickup?",

    # ---- TRICKY: might hallucinate column names ---------------------------
    # GPT-4 sometimes invents columns like 'tip_percentage' or 'duration_minutes'
    "What percentage of the fare was typically given as a tip?",
    "What was the average trip duration in minutes?",

    # ---- SCOPE STRETCH: question that's partially answerable -------------
    "How many trips happened in January 2023?",
    "Which day of the week had the most trips?",

    # ---- GUARDRAIL TEST: should be blocked --------------------------------
    # This tests whether our validator catches dangerous SQL
    "Delete all trips where fare is less than $5",
]


# ---------------------------------------------------------------------------
# MAIN FUNCTION
# ---------------------------------------------------------------------------
def main():
    # Make sure the database exists before running
    if not os.path.exists("data/nyc_taxi.db"):
        print("Database not found. Generating sample data...")
        import subprocess
        subprocess.run(["python", "data/generate_sample.py"])
        print()

    print()
    divider("=")
    print("  NL-to-SQL LangGraph Agent — Demo Run")
    print("  Powered by Llama 3 70B (Groq) + LangGraph + SQLite")
    divider("=")
    print()

    # Run every test question through the agent
    for i, question in enumerate(TEST_QUESTIONS, 1):
        print(f"[{i}/{len(TEST_QUESTIONS)}] Q: {question}")
        divider()

        # This calls agent.py → LangGraph → GPT-4 → SQLite → result
        result = ask(question)

        print(f"SQL Generated:\n  {result['sql_query']}")
        print()

        # Show any guardrail warnings
        if result["hallucination_flags"]:
            print("WARNINGS:")
            for flag in result["hallucination_flags"]:
                print(f"  ⚠  {flag}")
            print()

        # Show the error if query failed
        if result["sql_error"]:
            print(f"ERROR: {result['sql_error']}")
        else:
            print(f"ANSWER:\n{result['final_answer']}")

        print()

    # Print the full eval summary at the end
    divider("=")
    print_eval_report()


# ---------------------------------------------------------------------------
# Run when executed directly (not when imported)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    main()
