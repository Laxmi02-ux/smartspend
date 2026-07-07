"""
init_db.py
-----------
Creates a local SQLite database (smartspend.db) and fills it with sample
company expense transactions. A few large/odd amounts are seeded on purpose
so the anomaly detector in app.py has something real to catch.

Run this once before starting the Flask app:
    python init_db.py
"""

import sqlite3
import random
from datetime import datetime, timedelta

DB_NAME = "smartspend.db"

# Departments we simulate spending for
DEPARTMENTS = ["Marketing", "Engineering", "Sales", "HR", "Operations"]

# A realistic "normal" spending range per department (min, max) in dollars
NORMAL_RANGE = {
    "Marketing": (200, 3000),
    "Engineering": (100, 2500),
    "Sales": (150, 2000),
    "HR": (100, 1500),
    "Operations": (200, 2800),
}


def create_table(cursor):
    """Create the expenses table if it doesn't already exist."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            department TEXT NOT NULL,
            vendor TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL
        )
    """)


def generate_transactions(n=120):
    """Generate n randomised transactions, plus a handful of deliberate anomalies."""
    vendors = ["Google Ads", "AWS", "Office Depot", "Zoom", "Adobe", "Uber",
               "LinkedIn", "Slack", "Local Print Shop", "Airline Booking",
               "Conference Hall Rental", "Consultant Fees"]

    rows = []
    start_date = datetime(2026, 1, 1)

    for i in range(n):
        dept = random.choice(DEPARTMENTS)
        low, high = NORMAL_RANGE[dept]
        amount = round(random.uniform(low, high), 2)
        vendor = random.choice(vendors)
        date = (start_date + timedelta(days=random.randint(0, 180))).strftime("%Y-%m-%d")
        rows.append((dept, vendor, amount, date))

    # --- Deliberate anomalies (so the demo always has something to flag) ---
    rows.append(("Marketing", "Unknown Media Agency", 18500.00, "2026-03-12"))
    rows.append(("Engineering", "Cloud Overprovision LLC", 9999.99, "2026-02-20"))
    rows.append(("HR", "Unusual Consulting Retainer", 7200.00, "2026-04-01"))
    rows.append(("Operations", "Rush Freight Charges", 6100.50, "2026-05-15"))

    return rows


def main():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    create_table(cursor)

    # Clear out old data so re-running this script gives a clean demo each time
    cursor.execute("DELETE FROM expenses")

    rows = generate_transactions()
    cursor.executemany(
        "INSERT INTO expenses (department, vendor, amount, date) VALUES (?, ?, ?, ?)",
        rows
    )

    conn.commit()
    conn.close()
    print(f"✅ {DB_NAME} created/refreshed with {len(rows)} transactions.")


if __name__ == "__main__":
    main()
