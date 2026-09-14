import sys

with open("server.py", "r") as f:
    content = f.read()

# Replace get_all_users query
old_query = """        SELECT 
            u.user_id, u.first_name, u.last_name, u.contact_number, u.email,
            a.account_id, uc.login_code as activation_code,
            COALESCE(r.name, 'Homeowner') as role_name,
            un.id as unit_id,
            b.id as block_id,
            assoc.id as association_id,
            assoc.name as association_name,
            b.name as block_name,
            un.unit_number,
            assoc.address_line_1 as assoc_addr1,
            assoc.address_line_2 as assoc_addr2,
            assoc.city as assoc_city,
            assoc.state as assoc_state,
            assoc.pincode as assoc_pincode
        FROM user_details u
        LEFT JOIN accounts a ON u.user_id = a.user_id
        LEFT JOIN roles r ON COALESCE(a.role_id, u.role_id) = r.id
        LEFT JOIN user_codes uc ON u.code_id = uc.id
        LEFT JOIN units un ON u.unit_id = un.id
        LEFT JOIN blocks b ON un.block_id = b.id
        LEFT JOIN associations assoc ON b.association_id = assoc.id
        WHERE b.association_id IS NOT NULL"""

new_query = """        SELECT 
            u.user_id, u.first_name, u.last_name, u.contact_number, u.email,
            a.account_id, uc.login_code as activation_code,
            COALESCE(r.name, 'Homeowner') as role_name,
            un.id as unit_id,
            b.id as block_id,
            COALESCE(assoc.id, dir_assoc.id) as association_id,
            COALESCE(assoc.name, dir_assoc.name) as association_name,
            b.name as block_name,
            un.unit_number,
            COALESCE(assoc.address_line_1, dir_assoc.address_line_1) as assoc_addr1,
            COALESCE(assoc.address_line_2, dir_assoc.address_line_2) as assoc_addr2,
            COALESCE(assoc.city, dir_assoc.city) as assoc_city,
            COALESCE(assoc.state, dir_assoc.state) as assoc_state,
            COALESCE(assoc.pincode, dir_assoc.pincode) as assoc_pincode
        FROM user_details u
        LEFT JOIN accounts a ON u.user_id = a.user_id
        LEFT JOIN roles r ON COALESCE(a.role_id, u.role_id) = r.id
        LEFT JOIN user_codes uc ON u.code_id = uc.id
        LEFT JOIN units un ON u.unit_id = un.id
        LEFT JOIN blocks b ON un.block_id = b.id
        LEFT JOIN associations assoc ON b.association_id = assoc.id
        LEFT JOIN associations dir_assoc ON u.association_id = dir_assoc.id
        WHERE b.association_id IS NOT NULL OR u.association_id IS NOT NULL"""

content = content.replace(old_query, new_query)

# Add POST /admin/users endpoint
new_endpoint = """
@api_router.post("/admin/users")
async def admin_create_user(payload: AdminCreateUserIn, _: dict = Depends(require_admin)):
    code = None
    for _try in range(6):
        candidate = f"NST-{generate_code(6)}"
        exists = await db_fetchone("SELECT id FROM user_codes WHERE login_code=%s", (candidate,))
        if not exists:
            code = candidate
            break
    if code is None:
        raise HTTPException(status_code=500, detail="Could not generate a unique code.")
    code_id = await db_execute("INSERT INTO user_codes (login_code) VALUES (%s)", (code,))
    
    full_name = f"{payload.first_name} {payload.last_name}".strip()
    
    await db_execute(
        "INSERT INTO user_details (code_id, name, first_name, last_name, email, contact_number, role_id, association_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
        (code_id, full_name, payload.first_name, payload.last_name, payload.email.lower(), payload.contact_number, payload.role_id, payload.association_id),
    )
    
    # Optional: send email here if we want to mimic admin_create_member
    
    return {"ok": True, "message": "User created successfully", "activation_code": code}
"""

# Insert before get_all_users
content = content.replace("@api_router.get(\"/admin/users\")", new_endpoint + "\n@api_router.get(\"/admin/users\")")

with open("server.py", "w") as f:
    f.write(content)

