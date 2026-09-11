import sqlite3
conn = sqlite3.connect('skillbridge.db')
cursor = conn.cursor()
try:
    cursor.execute("SELECT * FROM alembic_version")
    rows = cursor.fetchall()
    print(f"Alembic version: {rows}")
except sqlite3.OperationalError as e:
    print(f"Error: {e}")
conn.close()