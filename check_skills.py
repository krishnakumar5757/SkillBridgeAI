import sqlite3
conn = sqlite3.connect('skillbridge.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM skills")
rows = cursor.fetchall()
print(f"Number of skills: {len(rows)}")
for row in rows:
    print(row)
conn.close()