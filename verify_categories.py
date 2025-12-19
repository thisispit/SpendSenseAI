import sqlite3
import os

db_path = os.path.join("backend", "transactions.db")
if not os.path.exists(db_path):
    print(f"Error: DB not found at {db_path}")
    # Try current dir
    if os.path.exists("transactions.db"):
        db_path = "transactions.db"

print(f"Checking DB at: {db_path}")
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT description, category, source_file FROM transactions WHERE description IN ('Uber Ride', 'Starbucks Coffee', 'Netflix Subscription')")
    rows = cursor.fetchall()
    print(f"Found {len(rows)} matching transactions:")
    for row in rows:
        print(f"  - {row[0]}: {row[1]} (from {row[2]})")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
