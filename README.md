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

## 🛠️ Tech Stack

- **Backend:** Python 3.x, Flask
- **Database:** SQLite
- **AI Integration:** Anthropic API (Claude)
- **Frontend:** HTML5, CSS3, JavaScript (Fetch API)

## 📡 API Endpoints

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `GET /api/transactions` | GET | Returns all transactions with calculated z-scores and risk flags |
| `GET /api/summary` | GET | Returns the AI-generated or fallback rule-based risk summary |

## 🚀 Future Roadmap

- [ ] Support for custom CSV/Excel transaction uploads
- [ ] Configurable z-score threshold settings via GUI
- [ ] Multi-currency support
- [ ] Export flagged report as PDF/CSV

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
