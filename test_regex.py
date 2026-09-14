import re

with open("server.py", "r") as f:
    content = f.read()

inserts = re.findall(r'(INSERT INTO[^"]+)', content, re.IGNORECASE)
for sql in inserts:
    match = re.search(r'INSERT INTO\s+([a-zA-Z0-9_]+)\s*\(([^)]+)\)\s*VALUES\s*\(([^)]+)\)', sql, re.IGNORECASE)
    if not match:
        print("FAILED TO MATCH:", sql)
print("Done")
