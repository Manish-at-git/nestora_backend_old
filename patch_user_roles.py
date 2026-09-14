import asyncio
import aiomysql
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
DB_USER = os.getenv("MYSQL_USER", "nestora")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "nestora_pass_2026")
DB_NAME = os.getenv("MYSQL_DB", "nestora")
DB_PORT = int(os.getenv("MYSQL_PORT", 3306))

async def alter_db():
    pool = await aiomysql.create_pool(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, db=DB_NAME, port=DB_PORT, autocommit=True
    )
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            try:
                await cur.execute("ALTER TABLE user_details ADD COLUMN role_id CHAR(36) NULL")
                print("Added role_id to user_details")
            except Exception as e:
                print(f"Skipping alter table user_details ADD role_id: {e}")
                
            try:
                await cur.execute("ALTER TABLE user_details ADD FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE SET NULL")
                print("Added foreign key for role_id to user_details")
            except Exception as e:
                print(f"Skipping foreign key: {e}")

def patch_server():
    path = "server.py"
    with open(path, "r") as f:
        c = f.read()

    # 1. Update GET /admin/users
    old_get_users = """        FROM user_details u
        LEFT JOIN accounts a ON u.user_id = a.user_id
        LEFT JOIN roles r ON a.role_id = r.id
        LEFT JOIN user_codes uc ON u.code_id = uc.id"""
    new_get_users = """        FROM user_details u
        LEFT JOIN accounts a ON u.user_id = a.user_id
        LEFT JOIN roles r ON COALESCE(a.role_id, u.role_id) = r.id
        LEFT JOIN user_codes uc ON u.code_id = uc.id"""
    c = c.replace(old_get_users, new_get_users)

    # 2. Update PUT /admin/users/{user_id}
    old_put_users = """    if payload.role_name:
        role = await db_fetchone("SELECT id FROM roles WHERE name=%s", (payload.role_name,))
        if role:
            await db_execute("UPDATE accounts SET role_id=%s WHERE user_id=%s", (role["id"], user_id))"""
    new_put_users = """    if payload.role_name:
        role = await db_fetchone("SELECT id FROM roles WHERE name=%s", (payload.role_name,))
        if role:
            await db_execute("UPDATE user_details SET role_id=%s WHERE user_id=%s", (role["id"], user_id))
            await db_execute("UPDATE accounts SET role_id=%s WHERE user_id=%s", (role["id"], user_id))"""
    c = c.replace(old_put_users, new_put_users)
    
    # 3. Update POST /auth/create-account
    old_create_acc_1 = """    details = await db_fetchone(
        "SELECT user_id FROM user_details WHERE code_id=%s", (code_row["id"],)
    )"""
    new_create_acc_1 = """    details = await db_fetchone(
        "SELECT user_id, role_id FROM user_details WHERE code_id=%s", (code_row["id"],)
    )"""
    c = c.replace(old_create_acc_1, new_create_acc_1)

    old_create_acc_2 = """    role = await db_fetchone("SELECT id FROM roles WHERE name='Homeowner'")
    role_id = role["id"] if role else None
    account_id = await db_execute(
        "INSERT INTO accounts (user_id, email, password_hash, role_id) VALUES (%s,%s,%s,%s)",
        (details["user_id"], payload.email.lower(), hash_password(payload.password), role_id),
    )"""
    new_create_acc_2 = """    role_id = details.get("role_id")
    if not role_id:
        role = await db_fetchone("SELECT id FROM roles WHERE name='Homeowner'")
        role_id = role["id"] if role else None
        
    account_id = await db_execute(
        "INSERT INTO accounts (user_id, email, password_hash, role_id) VALUES (%s,%s,%s,%s)",
        (details["user_id"], payload.email.lower(), hash_password(payload.password), role_id),
    )"""
    c = c.replace(old_create_acc_2, new_create_acc_2)

    # 4. Update POST /admin/associations/onboard
    old_onboard_tenant = """                t_user_id = await db_execute(
                    \"\"\"INSERT INTO user_details (name, first_name, last_name, email, contact_number, unit_id, address, code_id) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)\"\"\",
                    (f"{t_fname} {t_lname}", t_fname, t_lname, t_email, t_phone, u_id, full_address, t_code_id)
                )"""
    new_onboard_tenant = """                t_user_id = await db_execute(
                    \"\"\"INSERT INTO user_details (name, first_name, last_name, email, contact_number, unit_id, address, code_id, role_id) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)\"\"\",
                    (f"{t_fname} {t_lname}", t_fname, t_lname, t_email, t_phone, u_id, full_address, t_code_id, tenant_role_id)
                )"""
    c = c.replace(old_onboard_tenant, new_onboard_tenant)
    
    old_onboard_homeowner = """        user_id = await db_execute(
            \"\"\"INSERT INTO user_details (name, first_name, last_name, email, contact_number, unit_id, address, code_id) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)\"\"\",
            (f"{fname} {lname}", fname, lname, email, phone, u_id, full_address, code_id)
        )"""
    new_onboard_homeowner = """        user_id = await db_execute(
            \"\"\"INSERT INTO user_details (name, first_name, last_name, email, contact_number, unit_id, address, code_id, role_id) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)\"\"\",
            (f"{fname} {lname}", fname, lname, email, phone, u_id, full_address, code_id, homeowner_role_id)
        )"""
    c = c.replace(old_onboard_homeowner, new_onboard_homeowner)


    with open(path, "w") as f:
        f.write(c)
    print("Patched server.py")

async def main():
    await alter_db()
    patch_server()

if __name__ == "__main__":
    asyncio.run(main())
