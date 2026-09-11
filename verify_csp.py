import sys
sys.path.insert(0, r'D:\FOAI\Skillbridge\modules\module-4-career-readiness\backtracking-csp')
from csp import CSP
from solver import backtracking_search
from constraints import prerequisite_ordering, conflicting_skills

# 1. Prerequisite example
csp = CSP()
csp.add_variable('A', ['Basic'])
csp.add_variable('B', ['Basic'])
csp.add_variable('C', ['Basic'])
csp.add_constraint(lambda assigned: prerequisite_ordering(assigned, {'A': ['B'], 'B': ['C']}))

result = backtracking_search(csp, prerequisites={'A': ['B'], 'B': ['C']})

print('=== PREREQUISITE ORDER ===')
print('success:', result.success)
print('ordered_selected_skills:', result.ordered_selected_skills)
print('constraints_checked:', result.constraints_checked)
print('backtrack_count:', result.backtrack_count)
expected = ['C', 'B', 'A']
print('Expected order [C,B,A]:', result.ordered_selected_skills == expected)
print()

# 2. Backtracking example with conflict
csp2 = CSP()
csp2.add_variable('X', ['Value1', 'Value2'])
csp2.add_variable('Y', ['ValueA', 'ValueB'])
csp2.add_constraint(lambda assigned: conflicting_skills(assigned, {'X': ['ValueB'], 'Y': ['Value1']}))

result2 = backtracking_search(csp2)

print('=== BACKTRACKING WITH CONFLICT ===')
print('success:', result2.success)
print('ordered_selected_skills:', result2.ordered_selected_skills)
print('constraints_checked:', result2.constraints_checked)
print('backtrack_count:', result2.backtrack_count)
print('backtrack_count > 0:', result2.backtrack_count > 0)
print('constraints_checked > 0:', result2.constraints_checked > 0)