import sqlite3
import json

conn = sqlite3.connect('project_updates.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = [row[0] for row in cursor.fetchall()]

print("=" * 80)
print("DATABASE TABLES")
print("=" * 80)
for table in tables:
    print(f"\n[{table}]")
    cursor.execute(f"SELECT * FROM {table};")
    rows = cursor.fetchall()
    
    if not rows:
        print("  (empty)")
        continue
    
    # Get column names
    cursor.execute(f"PRAGMA table_info({table});")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"  Columns: {', '.join(columns)}")
    print(f"  Rows: {len(rows)}")
    print()
    
    for row in rows:
        row_dict = dict(row)
        for key, value in row_dict.items():
            if isinstance(value, str) and len(value) > 60:
                print(f"    {key}: {value[:60]}...")
            else:
                print(f"    {key}: {value}")
        print()

conn.close()
