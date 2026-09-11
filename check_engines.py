import sqlite3
import sys
sys.path.insert(0, r'D:\FOAI\Skillbridge\backend')

from sqlalchemy import inspect
from app.core.database import Base, engine, SessionLocal

# Check engine
insp = inspect(engine)
print('Engine tables:', insp.get_table_names())

# Check Base.metadata
print('Base.metadata tables:', list(Base.metadata.tables.keys()))

# Check the actual DB file
conn = sqlite3.connect('D:/FOAI/Skillbridge/backend/skillbridge.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print('DB file tables:', cursor.fetchall())
conn.close()