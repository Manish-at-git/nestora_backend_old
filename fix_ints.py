import re

with open("server.py", "r") as f:
    content = f.read()

# Replace any lingering id INT ... with CHAR(36)
content = re.sub(r'id\s+INT(\s+AUTO_INCREMENT)?\s+PRIMARY\s+KEY', r'id CHAR(36) PRIMARY KEY', content, flags=re.IGNORECASE)

keys = ['entity_type_id', 'entity_id', 'role_id', 'user_id', 'account_id', 'code_id', 'association_id', 'admin_id', 'event_id', 'block_id', 'unit_id', 'committee_id', 'service_request_id', 'sender_id', 'parent_id', 'feature_id', 'created_by']

for k in keys:
    content = re.sub(rf'{k}\s+INT', rf'{k} CHAR(36)', content, flags=re.IGNORECASE)

with open("server.py", "w") as f:
    f.write(content)

print("Fixed lingering INTs")
