import sqlite3
import sys
sys.path.insert(0, r'D:\FOAI\Skillbridge\backend')

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

engine = create_engine('sqlite:///./skillbridge.db')

with Session(engine) as session:
    # Test the career readiness logic directly
    from app.services.career_readiness import analyze_career_readiness
    
    # Test with John Doe's UUID and data_analyst role
    john_id = '301dbe08-e3c9-4470-bb55-583e60528924'
    
    try:
        result = analyze_career_readiness(john_id, 'data_analyst', session)
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
        print('  summary:', result['summary'])
        print('  roadmap_summary:', result['roadmap_summary'])
    except Exception as e:
        print(f'Error: {type(e).__name__}: {e}')
        import traceback
        traceback.print_exc()
    
    print()
    
    # Test with another student
    jane_id = 'c7e05131-4c48-463c-af50-f80ff5a2f548'
    try:
        result = analyze_career_readiness(jane_id, 'data_analyst', session)
        print('Career readiness result for Test2 User + data_analyst:')
        print('  readiness_score:', result['readiness_score'])
        print('  readiness_level:', result['readiness_level'])
    except Exception as e:
        print(f'Error: {type(e).__name__}: {e}')
    
    print()
    
    # Test with invalid student
    try:
        result = analyze_career_readiness('nonexistent-uuid', 'data_analyst', session)
        print('Career readiness result for nonexistent student:')
        print('  readiness_score:', result['readiness_score'])
        print('  readiness_level:', result['readiness_level'])
        print('  summary:', result['summary'])
    except Exception as e:
        print(f'Error: {type(e).__name__}: {e}')
    
    print()
    
    # Test with invalid role
    try:
        result = analyze_career_readiness(john_id, 'nonexistent-role', session)
        print('Career readiness result for nonexistent role:')
        print('  readiness_score:', result['readiness_score'])
        print('  readiness_level:', result['readiness_level'])
        print('  summary:', result['summary'])
    except Exception as e:
        print(f'Error: {type(e).__name__}: {e}')