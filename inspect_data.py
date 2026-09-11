import sqlite3
conn = sqlite3.connect('D:/FOAI/Skillbridge/backend/skillbridge.db')
cursor = conn.cursor()

# Check students
print('=== STUDENTS ===')
cursor.execute("SELECT id, first_name, last_name FROM students")
rows = cursor.fetchall()
print(f'Total students: {len(rows)}')
for row in rows:
    print('  %s: %s %s' % (row[0], row[1], row[2]))

# Check student_skills
print()
print('=== STUDENT SKILLS ===')
cursor.execute("SELECT student_id, skill_id, proficiency, source, confidence FROM student_skills")
rows = cursor.fetchall()
print(f'Total student_skills: {len(rows)}')
for row in rows:
    print('  %s: %s = %s (%s, conf=%.1f)' % (row[0], row[1], row[2], row[3], row[4]))

# Check skills
print()
print('=== SKILLS ===')
cursor.execute("SELECT id, name, category FROM skills")
rows = cursor.fetchall()
print(f'Total skills: {len(rows)}')
for row in rows:
    print('  %s: %s (%s)' % (row[0], row[1], row[2]))

conn.close()