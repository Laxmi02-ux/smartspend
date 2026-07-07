"""
app.py
------
SmartSpend AI backend.

Flow (this is the "data pipeline" you can explain in an interview):
1. Pull raw transaction rows out of the local SQLite file (smartspend.db).
2. Run a simple statistical check (z-score per department) to flag amounts
   that are unusually large compared to that department's normal spending.
3. Package the flagged + normal transactions as JSON for the frontend.
4. Optionally ask an LLM (Anthropic's Claude) to turn the flagged rows into
   a short, human-readable risk summary. If no API key is configured, a
   rule-based fallback summary is generated instead so the project still
   runs end-to-end with zero setup.
"""

import os
import sqlite3
import statistics

from flask import Flask, jsonify, send_from_directory

app = Flask(__name__, static_folder="static")

DB_NAME = "smartspend.db"

# How many standard deviations above the department average counts as "risky"
Z_SCORE_THRESHOLD = 1.5


# ---------------------------------------------------------------------------
# Step 1 + 2: Pull data from SQL and apply the math check
# ---------------------------------------------------------------------------
def fetch_transactions_with_risk():
    """
    Reads every transaction from the database, then computes a z-score for
    each transaction relative to its OWN department's average spending.
    A transaction is flagged 'risky' if its z-score exceeds the threshold.
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, department, vendor, amount, date FROM expenses ORDER BY date")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    # Group amounts by department so we can compute a mean/std per department
    dept_amounts = {}
    for row in rows:
        dept_amounts.setdefault(row["department"], []).append(row["amount"])

    dept_stats = {}
    for dept, amounts in dept_amounts.items():
        mean = statistics.mean(amounts)
        # need at least 2 points for a standard deviation; guard against divide-by-zero
        std = statistics.stdev(amounts) if len(amounts) > 1 else 0
        dept_stats[dept] = (mean, std)

    # Attach a risk flag + z-score to every transaction
    for row in rows:
        mean, std = dept_stats[row["department"]]
        if std > 0:
            z_score = (row["amount"] - mean) / std
        else:
            z_score = 0
        row["z_score"] = round(z_score, 2)
        row["is_risky"] = z_score >= Z_SCORE_THRESHOLD

    return rows


# ---------------------------------------------------------------------------
# Step 3: API endpoint the frontend calls to render the table
# ---------------------------------------------------------------------------
@app.route("/api/transactions")
def api_transactions():
    return jsonify(fetch_transactions_with_risk())


# ---------------------------------------------------------------------------
# Step 4: Ask an LLM to summarize the risky transactions in plain English
# ---------------------------------------------------------------------------
def build_fallback_summary(risky_rows):
    """A rule-based summary used when no ANTHROPIC_API_KEY is set, so the
    project still works with zero configuration."""
    if not risky_rows:
        return "No unusual spending detected. All transactions fall within normal ranges for their departments."

    total_flagged = sum(r["amount"] for r in risky_rows)
    depts = sorted(set(r["department"] for r in risky_rows))
    top = max(risky_rows, key=lambda r: r["amount"])

    return (
        f"⚠️ {len(risky_rows)} transaction(s) flagged as unusual, totaling "
        f"${total_flagged:,.2f} across {', '.join(depts)}. "
        f"The largest outlier is a ${top['amount']:,.2f} charge to '{top['vendor']}' "
        f"in {top['department']} on {top['date']}, which is significantly above that "
        f"department's typical spending (z-score {top['z_score']}). Recommend manual review."
    )


def build_ai_summary(risky_rows):
    """
    Calls Anthropic's Messages API to generate a natural-language risk summary.
    Falls back to the rule-based summary if no API key is present or the
    call fails for any reason (network, quota, etc.) so the demo never breaks.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return build_fallback_summary(risky_rows)

    try:
        import anthropic  # only imported if we actually have a key

        client = anthropic.Anthropic(api_key=api_key)

        transactions_text = "\n".join(
            f"- {r['department']}: ${r['amount']:.2f} to {r['vendor']} on {r['date']} "
            f"(z-score {r['z_score']})"
            for r in risky_rows
        ) or "None"

        message = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=200,
            messages=[{
                "role": "user",
                "content": (
                    "You are a financial risk analyst. Here are transactions flagged "
                    "as statistically unusual for their department:\n\n"
                    f"{transactions_text}\n\n"
                    "Write a short (3-4 sentence) plain-English risk summary a manager "
                    "could read in 10 seconds, highlighting the biggest concern first."
                )
            }]
        )
        return message.content[0].text

    except Exception as e:
        print(f"AI summary failed, using fallback. Reason: {e}")
        return build_fallback_summary(risky_rows)


@app.route("/api/summary")
def api_summary():
    rows = fetch_transactions_with_risk()
    risky_rows = [r for r in rows if r["is_risky"]]
    summary = build_ai_summary(risky_rows)
    return jsonify({
        "summary": summary,
        "risky_count": len(risky_rows),
        "total_transactions": len(rows),
    })


# ---------------------------------------------------------------------------
# Serve the frontend
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/static/<path:path>")
def static_files(path):
    return send_from_directory("static", path)


# Make sure the database exists (important on hosting platforms where we
# can't manually run `python init_db.py` first)
if not os.path.exists(DB_NAME):
    import init_db
    init_db.main()

if __name__ == "__main__":
    # PORT env var is set automatically by most hosting platforms (Render, Railway, etc.)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
