with open('backend/app/main.py', 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    print(f"{i:3}: {repr(line)}")