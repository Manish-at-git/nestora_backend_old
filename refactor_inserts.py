import re
import os

with open("server.py", "r") as f:
    content = f.read()

# Add import uuid if not present
if "import uuid" not in content:
    content = "import uuid\n" + content

# We want to find patterns like:
# id_var = await db_execute("INSERT INTO table (col1, col2) VALUES (%s, %s)", (val1, val2))
# and change them to:
# id_var = str(uuid.uuid4())
# await db_execute("INSERT INTO table (id, col1, col2) VALUES (%s, %s, %s)", (id_var, val1, val2))

def repl(match):
    prefix = match.group(1) # e.g. "    assoc_id ="
    table = match.group(2)
    cols = match.group(3)
    vals_str = match.group(4)
    params = match.group(5)
    
    # prefix can contain whitespace and var name
    var_name = prefix.split("=")[0].strip()
    indent = prefix.split(var_name)[0]
    
    new_cols = f"id, {cols}"
    new_vals = f"%s, {vals_str}"
    
    # Handle the params string. It might have newlines or multiple elements.
    # We just prepend our new var_name to it.
    if params.strip().startswith("("):
        # (val1, val2) -> (var_name, val1, val2)
        inner_params = params.strip()[1:]
        new_params = f"({var_name}, {inner_params}"
    else:
        # e.g. payload.tuple -> (var_name, *payload.tuple) or similar... 
        # Actually it's safer to just let manual fixes happen if this fails.
        new_params = f"({var_name},) + {params}"

    res = f"{indent}{var_name} = str(uuid.uuid4())\n{indent}await db_execute(\n{indent}    \"INSERT INTO {table} ({new_cols}) VALUES ({new_vals})\",\n{indent}    {new_params}\n{indent})"
    return res

# Regex to match:
# var_name = await db_execute("INSERT INTO table (cols) VALUES (vals)", params)
# (handling multi-line strings is tricky)
