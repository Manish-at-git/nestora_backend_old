import re

with open('server.py', 'r') as f:
    content = f.read()

# Replace: INSERT INTO notifications (id, account_id, title, message) VALUES (UUID(), %s, %s, %s)
content = content.replace(
    "INSERT INTO notifications (id, account_id, title, message)\n            VALUES (UUID(), %s, %s, %s)",
    "INSERT INTO notifications (account_id, title, message)\n            VALUES (%s, %s, %s)"
)

content = content.replace(
    "INSERT INTO notifications (id, account_id, title, message)\n                VALUES (UUID(), %s, %s, %s)",
    "INSERT INTO notifications (account_id, title, message)\n                VALUES (%s, %s, %s)"
)

content = content.replace(
    "INSERT INTO notifications (id, account_id, title, message)\n                    VALUES (UUID(), %s, %s, %s)",
    "INSERT INTO notifications (account_id, title, message)\n                    VALUES (%s, %s, %s)"
)

content = content.replace(
    "\"INSERT INTO notifications (id, account_id, title, message, visit_id) VALUES (%s, %s, %s, %s, %s)\",\n            (str(uuid.uuid4()),",
    "\"INSERT INTO notifications (account_id, title, message, visit_id) VALUES (%s, %s, %s, %s)\",\n            ("
)

# For 5513, 5707, 5737: INSERT INTO notifications (id, account_id, title, message, type) VALUES (UUID(), ...)
content = content.replace(
    "INSERT INTO notifications (id, account_id, title, message, type)\n                VALUES (UUID(), %s, %s, %s, %s)",
    "INSERT INTO notifications (account_id, title, message, type)\n                VALUES (%s, %s, %s, %s)"
)

content = content.replace(
    "INSERT INTO notifications (id, account_id, title, message, type)\n                    VALUES (UUID(), %s, %s, %s, %s)",
    "INSERT INTO notifications (account_id, title, message, type)\n                    VALUES (%s, %s, %s, %s)"
)

with open('server.py', 'w') as f:
    f.write(content)

print("Done")
