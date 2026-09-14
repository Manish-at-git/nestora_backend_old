import re
with open("server.py", "r") as f:
    content = f.read()

new_table = """
    CREATE TABLE IF NOT EXISTS board_members (
      id CHAR(36) PRIMARY KEY,
      association_id CHAR(36) NOT NULL,
      account_id CHAR(36) NOT NULL,
      term_start_date DATE NOT NULL,
      term_end_date DATE NOT NULL,
      status ENUM('active', 'past') DEFAULT 'active',
      created_by CHAR(36) NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (association_id) REFERENCES associations(id) ON DELETE CASCADE,
      FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE,
      FOREIGN KEY (created_by) REFERENCES accounts(account_id) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
"""

# inject before entities table
if "CREATE TABLE IF NOT EXISTS board_members" not in content:
    content = content.replace("CREATE TABLE IF NOT EXISTS entities", new_table + "    CREATE TABLE IF NOT EXISTS entities")
    with open("server.py", "w") as f:
        f.write(content)
