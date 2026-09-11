import sys
sys.path.insert(0, r'D:\FOAI\Skillbridge\backend')

import sys
sys.path.insert(0, r'D:\FOAI\Skillbridge\modules\module-3-learning-intelligence\astar')

# Test imports
from app.services.module3_learning import generate_learning_roadmap, get_student_skills_from_db, get_role_required_skills
from app.routes.module3_learning import router
print('OK All module3 imports successful')

# Test the A* algorithm directly
from astar.algorithm import a_star_search
from astar.graph import build_graph_from_roles
import json

skill_vocab_path = r'D:\FOAI\Skillbridge\data\skills\skills.json'
with open(skill_vocab_path, encoding='utf-8') as f:
    skill_vocab = json.load(f)

role_required_skills = [
    {'skill_id': 'SQL', 'minimum_proficiency': 'advanced', 'priority': 'critical', 'is_core': True},
    {'skill_id': 'Python', 'minimum_proficiency': 'intermediate', 'priority': 'critical', 'is_core': True},
    {'skill_id': 'React', 'minimum_proficiency': 'beginner', 'priority': 'nice_to_have', 'is_core': False},
    {'skill_id': 'Git', 'minimum_proficiency': 'intermediate', 'priority': 'critical', 'is_core': True},
    {'skill_id': 'System Design', 'minimum_proficiency': 'beginner', 'priority': 'important', 'is_core': False},
    {'skill_id': 'JavaScript', 'minimum_proficiency': 'intermediate', 'priority': 'important', 'is_core': False},
]

student_skills = {'Python': 'intermediate'}
student_skill_ids = set(student_skills.keys())
skill_graph = build_graph_from_roles(role_required_skills, student_skill_ids, skill_vocab_path)

result = a_star_search(
    student_skills=student_skills,
    target_role_id='data_analyst',
    role_required_skills=role_required_skills,
    skill_graph=skill_graph,
)

sql_in = 'SQL' in [s['skill_id'] for s in result['roadmap']['learning_steps']]
react_in = 'React' in [s['skill_id'] for s in result['roadmap']['learning_steps']]
print(f'OK A* search works: goal_reached={result["goal_reached"]}, cost={result["total_estimated_cost"]}')
print(f'OK SQL in roadmap: {sql_in}')
print(f'OK React in roadmap: {react_in}')