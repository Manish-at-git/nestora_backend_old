import os

SERVER_PATH = "server.py"

def replace_in_file(filepath, old_content, new_content):
    with open(filepath, "r") as f:
        content = f.read()
    
    if old_content in content:
        content = content.replace(old_content, new_content)
        with open(filepath, "w") as f:
            f.write(content)
        print("Replaced content successfully.")
    else:
        print("Old content not found.")

auth_me_old = """
        assoc_info = await db_fetchone(\"\"\"
            SELECT a.id as association_id, a.country as association_country
            FROM user_details ud
            JOIN units u ON ud.unit_id = u.id
            JOIN blocks b ON u.block_id = b.id
            JOIN associations a ON b.association_id = a.id
            WHERE ud.user_id = %s
        \"\"\", (account["user_id"],))
        
        if assoc_info:
            account["association_id"] = assoc_info["association_id"]
            account["association_country"] = assoc_info["association_country"]
"""

auth_me_new = """
        assoc_info = await db_fetchone(\"\"\"
            SELECT a.id as association_id, a.country as association_country, a.subscription_status, a.current_plan_id
            FROM user_details ud
            JOIN units u ON ud.unit_id = u.id
            JOIN blocks b ON u.block_id = b.id
            JOIN associations a ON b.association_id = a.id
            WHERE ud.user_id = %s
        \"\"\", (account["user_id"],))
        
        if assoc_info:
            account["association_id"] = assoc_info["association_id"]
            account["association_country"] = assoc_info["association_country"]
            account["subscription_status"] = assoc_info["subscription_status"]
            
            features = []
            if assoc_info["current_plan_id"]:
                f_rows = await db_fetchall(\"\"\"
                    SELECT f.name FROM subscription_plan_features spf
                    JOIN features f ON spf.feature_id = f.id
                    WHERE spf.plan_id = %s
                \"\"\", (assoc_info["current_plan_id"],))
                features = [r["name"] for r in f_rows]
            account["allowed_features"] = features
"""

admin_assoc_old = """
@api_router.get("/admin/associations")
async def get_all_associations(account: dict = Depends(require_role(["Super admin", "Admin", "Board member"]))):
    if account["role"] == "Super admin":
        return await db_fetchall("SELECT * FROM associations ORDER BY created_at DESC")
    elif account["role"] == "Admin":
        return await db_fetchall(
            \"\"\"
            SELECT a.* FROM associations a
            JOIN admin_associations aa ON a.id = aa.association_id
            WHERE aa.admin_id = %s
            ORDER BY a.created_at DESC
            \"\"\", (account["account_id"],)
        )
    else:
        # Board member
        assoc_id = await get_board_member_association(account["account_id"])
        if assoc_id:
            return await db_fetchall("SELECT * FROM associations WHERE id=%s", (assoc_id,))
        return []
"""

admin_assoc_new = """
@api_router.get("/admin/associations")
async def get_all_associations(account: dict = Depends(require_role(["Super admin", "Admin", "Board member"]))):
    rows = []
    if account["role"] == "Super admin":
        rows = await db_fetchall("SELECT * FROM associations ORDER BY created_at DESC")
    elif account["role"] == "Admin":
        rows = await db_fetchall(
            \"\"\"
            SELECT a.* FROM associations a
            JOIN admin_associations aa ON a.id = aa.association_id
            WHERE aa.admin_id = %s
            ORDER BY a.created_at DESC
            \"\"\", (account["account_id"],)
        )
    else:
        # Board member
        assoc_id = await get_board_member_association(account["account_id"])
        if assoc_id:
            rows = await db_fetchall("SELECT * FROM associations WHERE id=%s", (assoc_id,))
            
    # Inject allowed features for each association
    if rows:
        plan_features = await db_fetchall(\"\"\"
            SELECT spf.plan_id, f.name 
            FROM subscription_plan_features spf
            JOIN features f ON spf.feature_id = f.id
        \"\"\")
        feature_map = {}
        for pf in plan_features:
            feature_map.setdefault(pf["plan_id"], []).append(pf["name"])
            
        for r in rows:
            r["allowed_features"] = feature_map.get(r["current_plan_id"], []) if r.get("current_plan_id") else []
            
    return rows
"""

if __name__ == "__main__":
    replace_in_file(SERVER_PATH, auth_me_old, auth_me_new)
    replace_in_file(SERVER_PATH, admin_assoc_old, admin_assoc_new)
