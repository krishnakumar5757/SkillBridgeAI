import sys
sys.path.insert(0, r'D:\FOAI\Skillbridge\backend')

from fastapi.testclient import TestClient
from app.main import create_app

app = create_app()
client = TestClient(app)

# Use the existing API to check student data
from sqlalchemy import text
from app.core.database import SessionLocal

db = SessionLocal()
try:
    # List students
    result = db.execute(text('SELECT id, first_name, last_name FROM students'))
    students = result.fetchall()
    print(f'Students ({len(students)}):')
    for s in students:
        print(f'  {s[0]}: {s[1]} {s[2]}')
    
    # List student skills for student-001 if exists
    if students:
        sid = students[0][0]
        print(f'\nStudent skills for {sid}:')
        result = db.execute(text(f'SELECT skill_id, proficiency, source, confidence FROM student_skills WHERE student_id = "{sid}"'))
        ss = result.fetchall()
        for s in ss:
            print(f'  {s[0]}: proficiency={s[1]}, source={s[2]}, confidence={s[3]}')
finally:
    db.close()