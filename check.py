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

async def run():
    pool = await aiomysql.create_pool(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, db=DB_NAME, port=DB_PORT, autocommit=True
    )
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM employees")
            emps = await cur.fetchall()
            print(f"Employees: {len(emps)}")
            for e in emps:
                print(e['employee_id'], e['employee_id_number'])
                
            await cur.execute("SELECT account_id, email, user_id, employee_id, role_id FROM accounts")
            accts = await cur.fetchall()
            print(f"\nAccounts: {len(accts)}")
            for a in accts:
                print(a)
    pool.close()
    await pool.wait_closed()

if __name__ == "__main__":
    asyncio.run(run())
