import asyncio
import aiomysql
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
DB_USER = os.getenv("MYSQL_USER", "nestora")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "nestora_pass_2026")
DB_NAME = os.getenv("MYSQL_DB", "nestora")
DB_PORT = int(os.getenv("MYSQL_PORT", 3306))

ROLES_TO_MIGRATE = ['Super admin', 'Admin', 'CSR', 'Accountant', 'DataOps']

async def run():
    pool = await aiomysql.create_pool(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, db=DB_NAME, port=DB_PORT, autocommit=True
    )
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            format_strings = ','.join(['%s'] * len(ROLES_TO_MIGRATE))
            await cur.execute(f"""
                SELECT a.account_id, a.email, r.name as role_name 
                FROM accounts a
                JOIN roles r ON a.role_id = r.id
                WHERE r.name IN ({format_strings}) AND a.employee_id IS NULL
            """, tuple(ROLES_TO_MIGRATE))
            
            accounts = await cur.fetchall()
            print(f"Found {len(accounts)} accounts to generate employee records for.")
            
            counters = {}
            for row in accounts:
                acct_id = row['account_id']
                email = row['email']
                role_name = row['role_name']
                
                prefix = "NT" + role_name[:2].upper() + "#"
                if prefix not in counters:
                    await cur.execute(
                        "SELECT employee_id_number FROM employees WHERE employee_id_number LIKE %s ORDER BY LENGTH(employee_id_number) DESC, employee_id_number DESC LIMIT 1",
                        (prefix + "%",)
                    )
                    max_row = await cur.fetchone()
                    if max_row:
                        try:
                            counters[prefix] = int(max_row["employee_id_number"].split("#")[1])
                        except:
                            counters[prefix] = 0
                    else:
                        counters[prefix] = 0
                
                counters[prefix] += 1
                emp_id_num = f"{prefix}{counters[prefix]}"
                emp_id = str(uuid.uuid4())
                
                # Mock details since they don't exist
                name = email.split('@')[0].capitalize()
                
                await cur.execute("""
                    INSERT INTO employees 
                    (employee_id, employee_id_number, name, address, email, contact_number, first_name, last_name)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (emp_id, emp_id_num, name, "N/A", email, "0000000000", name, ""))
                
                await cur.execute("UPDATE accounts SET employee_id=%s WHERE account_id=%s", (emp_id, acct_id))
                print(f"Assigned {emp_id_num} to {email}")

    pool.close()
    await pool.wait_closed()

if __name__ == "__main__":
    asyncio.run(run())
