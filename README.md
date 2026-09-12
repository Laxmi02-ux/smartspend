# SmartSpend AI

A local expense anomaly detector: it pulls transactions from a SQLite database,
flags unusually large charges with a statistical check, asks an LLM to summarize
the risk in plain English, and displays everything in a color-coded web page.

## How it works (the pipeline)

1. **Database** — `smartspend.db` (SQLite) holds a table of transactions:
   department, vendor, amount, date. `init_db.py` creates it and seeds ~120
   realistic transactions plus a few deliberate anomalies so the demo always
   has something to catch.
2. **Math check** — `app.py` groups transactions by department and computes a
   **z-score** for each transaction (how many standard deviations it is from
   that department's average spend). Anything with z-score ≥ 1.5 is flagged risky.
3. **AI summary** — the flagged transactions are sent to Claude (Anthropic API)
   with a prompt asking for a short manager-friendly risk summary. If you don't
   have an API key set, it automatically falls back to a rule-based summary,
   so the whole project still works out of the box.
4. **Frontend** — `index.html` + `static/script.js` fetch both API endpoints
   and render a table (risky rows highlighted in red) plus the summary text.

## Project structure

```
smartspend/
├── app.py            # Flask backend: API + anomaly logic + AI summary
├── init_db.py         # Creates and seeds smartspend.db
├── index.html         # Frontend page
├── static/
│   ├── style.css
│   └── script.js
├── requirements.txt
└── README.md
```

## Setup & running it

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create the database (only needs to be run once, or again to reset data)
python init_db.py

# 3. (Optional) enable real AI summaries by setting your Anthropic API key
export ANTHROPIC_API_KEY="your-key-here"     # macOS/Linux
set ANTHROPIC_API_KEY=your-key-here          # Windows (cmd)

# 4. Start the server
python app.py
```

- Let users upload their own CSV of transactions instead of using seed data.
- Add authentication so different managers see only their department.
