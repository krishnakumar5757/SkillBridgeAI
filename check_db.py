import sqlite3
import sys
sys.path.insert(0, r'D:\FOAI\Skillbridge\backend')

# Check the DB file directly
conn = sqlite3.connect('skillbridge.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('Tables in DB file:', tables)
conn.close()