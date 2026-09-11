import sys
sys.path.insert(0, r'D:\FOAI\Skillbridge\backend')

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

engine = create_engine('sqlite:///./skillbridge.db')

with Session(engine) as session:
    result = session.execute(text('SELECT id, first_name FROM students LIMIT 5'))
    rows = result.mappings().all()
    print(f'Students in DB: {len(rows)}')
    for row in rows:
        print(f'  {row[\"id\"]}: {row[\"first_name\"]}')
    
    # Now test the career readiness logic directly
    from app.services.career_readiness import analyze_career_readiness
    
    # Test with student-001 and data_analyst
    try:
        result = analyze_career_readiness('student-001', 'data_analyst', session)
        print()
        print('Career readiness result:')
        print(f'  readiness_score: {result["readiness_score"]}')
        print(f'  readiness_level: {result["readiness_level"]}')
        print(f'  total_required: {result["total_required_skills"]}')
        print(f'  skills_met: {len(result["skills_met"])}')
        print(f'  skills_missing: {len(result["skills_missing"])}')
        print(f'  skills_below: {len(result["skills_below"])}')
        print(f'  coverage: {result["coverage_percentage"]}%')
        print(f'  proficiency: {result["proficiency_percentage"]}%')
        print(f'  summary: {result["summary"][:100]}')
    except Exception as e:
        print(f'Error: {type(e).__name__}: {e}')
        import traceback
        traceback.print_exc()