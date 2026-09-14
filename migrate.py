import re

with open("server.py", "r") as f:
    content = f.read()

# Replace CREATE TABLE id INT AUTO_INCREMENT PRIMARY KEY
content = re.sub(
    r"id INT AUTO_INCREMENT PRIMARY KEY",
    r"id CHAR(36) PRIMARY KEY",
    content
)

# Also need to replace all INT foreign keys to CHAR(36)
content = re.sub(r"entity_id INT", r"entity_id CHAR(36)", content)
content = re.sub(r"role_id INT", r"role_id CHAR(36)", content)
content = re.sub(r"user_id INT", r"user_id CHAR(36)", content)
content = re.sub(r"account_id INT", r"account_id CHAR(36)", content)
content = re.sub(r"code_id INT", r"code_id CHAR(36)", content)
content = re.sub(r"association_id INT", r"association_id CHAR(36)", content)
content = re.sub(r"admin_id INT", r"admin_id CHAR(36)", content)
content = re.sub(r"event_id INT", r"event_id CHAR(36)", content)
content = re.sub(r"block_id INT", r"block_id CHAR(36)", content)
content = re.sub(r"unit_id INT", r"unit_id CHAR(36)", content)
content = re.sub(r"committee_id INT", r"committee_id CHAR(36)", content)
content = re.sub(r"service_request_id INT", r"service_request_id CHAR(36)", content)
content = re.sub(r"sender_id INT", r"sender_id CHAR(36)", content)

# But wait, there are type hints int -> str
content = re.sub(r": int", r": str", content)

with open("server.py", "w") as f:
    f.write(content)

with open("setup_associations_db.py", "r") as f:
    assoc = f.read()
assoc = re.sub(r"id INT AUTO_INCREMENT PRIMARY KEY", r"id CHAR(36) PRIMARY KEY", assoc)
assoc = re.sub(r"([a-z_]+_id)\s+INT", r"\1 CHAR(36)", assoc)
with open("setup_associations_db.py", "w") as f:
    f.write(assoc)

with open("setup_service_requests_db.py", "r") as f:
    sr = f.read()
sr = re.sub(r"id INT AUTO_INCREMENT PRIMARY KEY", r"id CHAR(36) PRIMARY KEY", sr)
sr = re.sub(r"([a-z_]+_id)\s+INT", r"\1 CHAR(36)", sr)
with open("setup_service_requests_db.py", "w") as f:
    f.write(sr)

print("Schema updated successfully.")
