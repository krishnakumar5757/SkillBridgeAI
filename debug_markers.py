with open('backend/app/main.py', 'r') as f:
    lines = f.readlines()

print("Total lines:", len(lines))
for i, line in enumerate(lines):
    stripped = line.strip()
    if stripped == '# ---------------------------------------------------------------------------':
        if i+2 < len(lines):
            if lines[i+1].strip() == '' and lines[i+2].strip() == '# Database Seeding':
                print(f"Found start marker at line {i}: {lines[i].rstrip()}")
                print(f"  Next line: {lines[i+1].rstrip()}")
                print(f"  Next next line: {lines[i+2].rstrip()}")
            if lines[i+1].strip() == '' and lines[i+2].strip() == '# Application Lifespan':
                print(f"Found end marker at line {i}: {lines[i].rstrip()}")
                print(f"  Next line: {lines[i+1].rstrip()}")
                print(f"  Next next line: {lines[i+2].rstrip()}")