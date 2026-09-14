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
                await cur.execute("ALTER TABLE units ADD COLUMN is_rented BOOLEAN DEFAULT FALSE")
                print("Added is_rented column to units table.")
            except Exception as e:
                print(f"Column might already exist: {e}")

def patch_server():
    path = "server.py"
    with open(path, "r") as f:
        c = f.read()

    # 1. Update onboard_association to set is_rented
    old_rented = """        # Check if Rented
        rented = str(row.get("Rented", "")).strip().title()
        if rented == "Yes":
            t_fname = str(row.get("Tenant First Name", ""))"""
    new_rented = """        # Check if Rented
        rented = str(row.get("Rented", "")).strip().title()
        if rented == "Yes":
            await db_execute("UPDATE units SET is_rented=TRUE WHERE id=%s", (u_id,))
            t_fname = str(row.get("Tenant First Name", ""))"""
    c = c.replace(old_rented, new_rented)

    # 2. Update get_association_stats query
    old_stats = """    rented = await db_fetchone('''
        SELECT count(DISTINCT u.id) as count 
        FROM units u 
        JOIN blocks b ON u.block_id = b.id 
        JOIN user_details ud ON ud.unit_id = u.id
        JOIN accounts a ON a.user_id = ud.user_id
        JOIN roles r ON r.id = a.role_id
        WHERE b.association_id = %s AND LOWER(r.name) = 'tenant'
    ''', (id,))"""
    new_stats = """    rented = await db_fetchone('''
        SELECT count(*) as count 
        FROM units u 
        JOIN blocks b ON u.block_id = b.id 
        WHERE b.association_id = %s AND u.is_rented = TRUE
    ''', (id,))"""
    c = c.replace(old_stats, new_stats)

    with open(path, "w") as f:
        f.write(c)
    print("Patched server.py")

async def main():
    await alter_db()
    patch_server()

if __name__ == "__main__":
    asyncio.run(main())
