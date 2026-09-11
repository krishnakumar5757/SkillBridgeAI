import sys
sys.path.insert(0, r'D:\FOAI\Skillbridge\backend')

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.services.career_readiness import analyze_career_readiness

# Create a session
db = SessionLocal()

# Test with John Doe's UUID and data_analyst role
try:
    result = analyze_career_readiness('301dbe08-e3c9-4470-bb55-583e60528924', 'data_analyst', db)
    print('Career readiness result for John Doe + data_analyst:')
    print('  readiness_score:', result['readiness_score'])
    print('  readiness_level:', result['readiness_level'])
    print('  total_required:', result['total_required_skills'])
    print('  skills_met:', len(result['skills_met']))
    print('  skills_missing:', len(result['skills_missing']))
    print('  skills_below:', len(result['skills_below']))
    print('  coverage:', result['coverage_percentage'], '%')
    print('  proficiency:', result['proficiency_percentage'], '%')
    print('  strengths:', result['strengths'])
    print('  priority_gaps:', result['priority_gaps'])
    print('  recommendations:', result['recommendations'])
    print('  summary:', result['summary'][:100])
except Exception as e:
    print(f'Error: {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()

db.close()