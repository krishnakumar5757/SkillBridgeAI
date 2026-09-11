import sys
sys.path.insert(0, r'D:\FOAI\Skillbridge\backend')

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

engine = create_engine('sqlite:///D:/FOAI/Skillbridge/backend/skillbridge.db')
session = Session(engine)

from app.services.career_readiness import analyze_career_readiness

# Test with John Doe + data_analyst
result = analyze_career_readiness('301dbe08-e3c9-4470-bb55-583e60528924', 'data_analyst', session)
print('=== REVISED FORMULA VERIFICATION ===')
print()
print('Input data:')
print(f'  Student: 301dbe08-e3c9-4470-bb55-583e60528924 (John Doe)')
print(f'  Role: data_analyst')
print(f'  Student has: Python (intermediate)')
print()

# Manually compute the revised formula
total_required = result['total_required_skills']
skills_met = len(result['skills_met'])
skills_below = len(result['skills_below'])
skills_missing = len(result['skills_missing'])

from app.utils.constants import PROFICIENCY_LEVELS, PROFICIENCY_BEGINNER

# 1. Coverage (40% weight) - includes both skills_met AND skills_below
acquired_count = skills_met + skills_below
coverage_fraction = acquired_count / total_required
coverage_percentage = coverage_fraction * 100

# 2. Proficiency match (40% weight) - only skills_met (meet/exceed required)
proficient_count = 0
total_profiled = 0
for s in result['skills_met']:
    current = s['current_proficiency']
    required = PROFICIENCY_LEVELS.get(s['required_proficiency'], 1)
    if current >= required:
        proficient_count += 1
    total_profiled += 1

proficient_fraction = (proficient_count / total_profiled) if total_profiled > 0 else 1.0
proficiency_percentage = proficient_fraction * 100

# 3. Core skill coverage (15% weight)
role_required_skills = [
    {'skill_id': 'SQL', 'minimum_proficiency': 'advanced', 'priority': 'critical', 'is_core': True},
    {'skill_id': 'Python', 'minimum_proficiency': 'intermediate', 'priority': 'critical', 'is_core': True},
    {'skill_id': 'React', 'minimum_proficiency': 'beginner', 'priority': 'nice_to_have', 'is_core': False},
    {'skill_id': 'Git', 'minimum_proficiency': 'intermediate', 'priority': 'critical', 'is_core': True},
    {'skill_id': 'System Design', 'minimum_proficiency': 'beginner', 'priority': 'important', 'is_core': False},
    {'skill_id': 'JavaScript', 'minimum_proficiency': 'intermediate', 'priority': 'important', 'is_core': False},
]
total_core = sum(1 for s in role_required_skills if s.get('is_core', False))
core_skills_met = sum(1 for s in result['skills_met'] if s.get('is_core', False))
core_fraction = (core_skills_met / total_core) if total_core > 0 else 1.0
core_percentage = core_fraction * 100

# 4. Gap penalty (5% weight)
gap_penalty = (skills_missing * 3 + skills_below * 1) * (5.0 / total_required) if total_required > 0 else 0.0
gap_penalty = min(gap_penalty, 5.0)

# 5. Final score - weighted sum with actual weights
weighted_score = (coverage_percentage * 0.40
                + proficiency_percentage * 0.40
                + core_percentage * 0.15
                - gap_penalty)
final_score = max(0.0, min(100.0, round(weighted_score)))

print('Revised formula computation:')
print()
print(f'  1. Coverage (40%): acquired={skills_met}+{skills_below}={acquired_count}/{total_required}')
print(f'     coverage_fraction = {acquired_count}/{total_required} = {coverage_fraction:.4f}')
print(f'     coverage_percentage = {coverage_percentage:.2f}%')
print(f'     Reported: {result["coverage_percentage"]}%')
print()
print(f'  2. Proficiency (40%): proficient_count={proficient_count}/{total_profiled}')
print(f'     proficient_fraction = {proficient_count}/{total_profiled} = {proficient_fraction:.4f}')
print(f'     proficiency_percentage = {proficiency_percentage:.2f}%')
print(f'     Reported: {result["proficiency_percentage"]}%')
print()
print(f'  3. Core coverage (15%): core_skills_met={core_skills_met}/{total_core}')
print(f'     core_fraction = {core_skills_met}/{total_core} = {core_fraction:.4f}')
print(f'     core_percentage = {core_percentage:.2f}%')
print()
print(f'  4. Gap penalty (5%): missing={skills_missing}, below={skills_below}')
print(f'     gap_penalty = ({skills_missing} * 3 + {skills_below} * 1) * (5.0 / {total_required})')
print(f'     = {skills_missing * 3 + skills_below * 1} * {5.0}/{total_required} = {gap_penalty:.2f} (capped)')
print()
print(f'  5. Final score:')
print(f'     weighted_score = {coverage_percentage:.2f} * 0.40 + {proficiency_percentage:.2f} * 0.40 + {core_percentage:.2f} * 0.15 - {gap_penalty:.2f}')
print(f'     = {coverage_percentage:.2f} * 0.40 + {proficiency_percentage:.2f} * 0.40 + {core_percentage:.2f} * 0.15 - {gap_penalty:.2f}')
print(f'     = {coverage_percentage*0.40:.2f} + {proficiency_percentage*0.40:.2f} + {core_percentage*0.15:.2f} - {gap_penalty:.2f}')
print(f'     = {coverage_percentage*0.40 + proficiency_percentage*0.40 + core_percentage*0.15 - gap_penalty:.2f}')
print(f'     final_score = max(0, min(100, round({coverage_percentage*0.40 + proficiency_percentage*0.40 + core_percentage*0.15 - gap_penalty:.2f}))) = {final_score}')
print(f'     Reported readiness_score: {result["readiness_score"]}')
print(f'     Reported readiness_level: {result["readiness_level"]}')
print()

# Consistency checks
cov_ok = result['coverage_percentage'] == round(coverage_fraction * 100, 1)
prof_ok = result['proficiency_percentage'] == round(proficient_fraction * 100, 1)
score_ok = result['readiness_score'] == final_score
level_ok = result['readiness_level'] in ['Ready', 'Nearly Ready', 'Developing', 'Not Ready']

print('=== CONSISTENCY CHECK ===')
print(f'  Coverage consistent: {cov_ok}')
print(f'  Proficiency consistent: {prof_ok}')
print(f'  Score matches formula: {score_ok}')
print(f'  Level valid: {level_ok}')
print()

if cov_ok and prof_ok and score_ok and level_ok:
    print('ALL CONSISTENCY CHECKS PASS')
else:
    print('SOME CONSISTENCY CHECKS FAIL')

session.close()