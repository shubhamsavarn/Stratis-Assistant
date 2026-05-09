import sqlite3
import os

db_path = 'data/insights_assistant.db'
if not os.path.exists(db_path):
    print(f"Database {db_path} not found.")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table';")
    for name, sql in cursor.fetchall():
        print(f"--- Table: {name} ---")
        print(sql)
        # Also get a sample of data to help the LLM understand formats
        cursor.execute(f"SELECT * FROM {name} LIMIT 2;")
        cols = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        print(f"Columns: {cols}")
        print(f"Sample: {rows}\n")
    conn.close()
