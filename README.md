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

Then open **http://127.0.0.1:5000** in your browser.

> No API key? No problem — you'll still get a solid rule-based summary,
> and everything else (table, red-flag highlighting, math) works identically.

## Talking points for interviews

- "I built a local pipeline that moves financial records from a relational
  database, applies statistical logic (z-scores), and structures the output
  for an LLM API."
- Explains **why z-scores**: a flat "amount > $5000" rule doesn't work because
  departments spend very differently — Engineering's $9,000 AWS bill is normal,
  but a $9,000 charge in HR is a huge outlier. Z-scores compare each transaction
  to its *own department's* normal range.
- Explains the **graceful degradation** design: the AI call is wrapped in a
  try/except with a rule-based fallback, so a missing API key or network issue
  never breaks the app — a good example of defensive coding.

## Ideas to extend it later

- Swap the flat file for a real Postgres/MySQL database.
- Add a date-range filter or department filter on the frontend.
- Let users upload their own CSV of transactions instead of using seed data.
- Add authentication so different managers see only their department.
