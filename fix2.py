import re

with open('server.py', 'r') as f:
    content = f.read()

content = content.replace(
    "INSERT INTO notifications (id, account_id, title, message, type)\n                    VALUES (%s, %s, %s, %s, %s)",
    "INSERT INTO notifications (account_id, title, message, type)\n                    VALUES (%s, %s, %s, %s)"
)

content = content.replace(
    "(str(uuid.uuid4()), r[\"account_id\"], \"Staff Entry\"",
    "(r[\"account_id\"], \"Staff Entry\""
)

content = content.replace(
    "(str(uuid.uuid4()), r[\"account_id\"], \"Staff Exit\"",
    "(r[\"account_id\"], \"Staff Exit\""
)

with open('server.py', 'w') as f:
    f.write(content)
print("Fixed")
