import sys

with open("server.py", "r") as f:
    content = f.read()

old_query = """        SELECT ud.user_id, ud.code_id, ud.name, ud.address, ud.email, ud.contact_number, uc.login_code,
               assoc.address_line_1, assoc.address_line_2,
               assoc.city, assoc.state, assoc.pincode,
               b.name as block_name, un.unit_number
        FROM user_details ud 
        JOIN user_codes uc ON uc.id=ud.code_id
        LEFT JOIN units un ON ud.unit_id = un.id
        LEFT JOIN blocks b ON un.block_id = b.id
        LEFT JOIN associations assoc ON b.association_id = assoc.id"""

new_query = """        SELECT ud.user_id, ud.code_id, ud.name, ud.address, ud.email, ud.contact_number, uc.login_code,
               assoc.name as association_name,
               assoc.address_line_1, assoc.address_line_2,
               assoc.city, assoc.state, assoc.pincode,
               b.name as block_name, un.unit_number
        FROM user_details ud 
        JOIN user_codes uc ON uc.id=ud.code_id
        LEFT JOIN units un ON ud.unit_id = un.id
        LEFT JOIN blocks b ON un.block_id = b.id
        LEFT JOIN associations assoc ON b.association_id = assoc.id OR ud.association_id = assoc.id"""

content = content.replace(old_query, new_query)

# Now fix the address construction
old_address_logic = """    if not row["address"]:
        parts = []
        if row.get("block_name") and row.get("unit_number"):
            parts.append(f"Block {row['block_name']} - Unit {row['unit_number']}")
        if row.get("address_line_1"):
            parts.append(row["address_line_1"])
        if row.get("address_line_2"):
            parts.append(row["address_line_2"])"""

new_address_logic = """    if not row["address"]:
        parts = []
        if row.get("block_name") and row.get("unit_number"):
            parts.append(f"Block {row['block_name']} - Unit {row['unit_number']}")
        elif row.get("association_name"):
            parts.append(row["association_name"])
            
        if row.get("address_line_1"):
            parts.append(row["address_line_1"])
        if row.get("address_line_2"):
            parts.append(row["address_line_2"])"""

content = content.replace(old_address_logic, new_address_logic)

with open("server.py", "w") as f:
    f.write(content)

