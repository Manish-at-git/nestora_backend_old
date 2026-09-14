import re
import os

with open('server.py', 'r') as f:
    lines = f.readlines()

new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # We are looking for lines with:  var_name = await db_execute(
    # followed by "INSERT INTO ...
    
    match = re.search(r'^(\s+)([a-zA-Z0-9_]+)\s*=\s*await db_execute\(', line)
    if match and "INSERT INTO" in ''.join(lines[i:i+4]):
        indent = match.group(1)
        var_name = match.group(2)
        
        # Check if the query spans multiple lines
        query_end = i
        while query_end < len(lines) and ")" not in lines[query_end]:
            query_end += 1
            
        full_statement = "".join(lines[i:query_end+1])
        
        # Parse full statement
        insert_match = re.search(r'INSERT INTO ([a-zA-Z0-9_]+)\s*\(([^)]+)\)\s*VALUES\s*\(([^)]+)\)', full_statement)
        if insert_match:
            table = insert_match.group(1)
            cols = insert_match.group(2)
            vals = insert_match.group(3)
            
            # Reconstruct
            new_cols = f"id, {cols}"
            new_vals = f"%s, {vals}"
            
            # Now replacing in the original string
            new_statement = full_statement.replace(f"({cols})", f"({new_cols})", 1)
            new_statement = new_statement.replace(f"({vals})", f"({new_vals})", 1)
            
            # Also we need to inject var_name into the parameter tuple
            # Parameter tuple comes after the SQL string.
            # E.g. , (user_id, email, ...))
            # This is hard to do with regex across multiple lines.
            
    # Simple strategy: just change db_execute to support returning the UUID
    
    new_lines.append(line)
    i += 1

