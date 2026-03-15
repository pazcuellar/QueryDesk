"""
eval_logger.py
--------------
Records every question the agent processes into a structured log file.

Each log entry captures:
  - the question asked
  - the SQL GPT-4 generated
  - whether it succeeded or failed
  - any hallucination warnings
  - a timestamp

After running a batch of questions, call print_eval_report() to see
a summary of what worked, what failed, and what was hallucinated.
"""

import json
import os
from datetime import datetime

LOG_PATH = "logs/eval_log.jsonl"   # .jsonl = one JSON object per line

# ---------------------------------------------------------------------------
# log_turn — called automatically by the agent after every question
# ---------------------------------------------------------------------------
def log_turn(
    question:            str,
    sql_generated:       str,
    sql_error:           str,
    result_preview:      str,
    hallucination_flags: list,
):
    """
    Appends one log entry to the eval log file.
    Called automatically by the agent — you don't need to call this manually.
    """
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)

    entry = {
        "timestamp":            datetime.now().isoformat(),
        "question":             question,
        "sql_generated":        sql_generated,
        "success":              sql_error is None,          # True if no error
        "sql_error":            sql_error,
        "hallucination_flags":  hallucination_flags,
        "had_hallucination":    len(hallucination_flags) > 0,
        "result_preview":       result_preview,
    }

    # Append to file (one JSON per line = easy to parse later)
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")


# ---------------------------------------------------------------------------
# print_eval_report — run this after a batch to see how the agent performed
# ---------------------------------------------------------------------------
def print_eval_report():
    """
    Reads the eval log and prints a summary report.
    Shows: total questions, success rate, hallucination rate, all failures.

    Run with:  python eval_logger.py
    """
    if not os.path.exists(LOG_PATH):
        print("No eval log found. Run some questions first via main.py")
        return

    entries = []
    with open(LOG_PATH, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))

    if not entries:
        print("Log file is empty.")
        return

    total         = len(entries)
    successes     = sum(1 for e in entries if e["success"])
    hallucinations = sum(1 for e in entries if e["had_hallucination"])
    failures      = [e for e in entries if not e["success"]]

    print("\n" + "="*60)
    print("  EVAL REPORT — NL-to-SQL LangGraph Agent")
    print("="*60)
    print(f"  Total questions run : {total}")
    print(f"  Successful queries  : {successes}  ({100*successes//total}%)")
    print(f"  Failed queries      : {total - successes}  ({100*(total-successes)//total}%)")
    print(f"  Hallucination flags : {hallucinations}  ({100*hallucinations//total}%)")
    print("="*60)

    if failures:
        print("\n  FAILURES:")
        for e in failures:
            print(f"\n  Q: {e['question']}")
            print(f"  SQL: {e['sql_generated']}")
            print(f"  Error: {e['sql_error']}")

    hallucinated = [e for e in entries if e["had_hallucination"]]
    if hallucinated:
        print("\n  HALLUCINATION FLAGS:")
        for e in hallucinated:
            print(f"\n  Q: {e['question']}")
            print(f"  SQL: {e['sql_generated']}")
            for flag in e["hallucination_flags"]:
                print(f"  FLAG: {flag}")

    print("\n  Full log saved to:", LOG_PATH)
    print("="*60 + "\n")


# ---------------------------------------------------------------------------
# Allow running this file directly to see the report
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print_eval_report()
