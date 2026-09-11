import sys
sys.path.insert(0, r'D:\FOAI\Skillbridge\modules\module-3-learning-intelligence\astar')
sys.path.insert(0, r'D:\FOAI\Skillbridge\backend')

from app.services.module3_learning import generate_learning_roadmap
import sys
sys.path.insert(0, r'D:\FOAI\Skillbridge\modules\module-3-learning-intelligence\astar')
sys.path.insert(0, r'D:\FOAI\Skillbridge\backend')

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

class MockDB:
    pass
db = MockDB()

student_id = 'student-001'
role_id = 'data_analyst'
roadmap_result = generate_learning_roadmap(student_id=student_id, role_id=role_id, db=db)

print(f'OK generate_learning_roadmap works')
print(f'  goal_reached: {roadmap_result["goal_reached"]}')
print(f'  total_estimated_cost: {roadmap_result["total_estimated_cost"]}')
roadmap = roadmap_result['roadmap']
steps = roadmap['learning_steps']
sql_name = 'SQL'
react_name = 'React'
sql_in = sql_name in [s['skill_id'] for s in steps]
react_in = react_name in [s['skill_id'] for s in steps]
print(f'  SQL in roadmap: {sql_in}')
print(f'  React in roadmap: {react_in}')
python_reason = steps[0]['reason']
print(f'  Python already possessed: {python_reason == "Already possessed"}')
print(f'  nodes_expanded: {roadmap_result["nodes_expanded"]}')
print(f'  search_depth: {roadmap_result["search_depth"]}')