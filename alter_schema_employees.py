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

async def run_migration():
    pool = await aiomysql.create_pool(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, db=DB_NAME, port=DB_PORT, autocommit=True
    )
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            # 1. Ensure schemas exist
            # Create employees table
            await cur.execute("""
            CREATE TABLE IF NOT EXISTS employees (
              employee_id CHAR(36) PRIMARY KEY,
              employee_id_number VARCHAR(50) UNIQUE NOT NULL,
              name VARCHAR(150) NOT NULL,
              address VARCHAR(255) NOT NULL,
              email VARCHAR(150) NOT NULL,
              contact_number VARCHAR(30) NOT NULL,
              first_name VARCHAR(100),
              last_name VARCHAR(100),
              address_line_1 VARCHAR(255),
              address_line_2 VARCHAR(255),
              city VARCHAR(100),
              state VARCHAR(100),
              pincode VARCHAR(20),
              emergency_contact_name VARCHAR(150),
              emergency_contact_number VARCHAR(30),
              id_proof_url VARCHAR(255),
              onboard_date DATE,
              end_date DATE,
              created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            print("Verified 'employees' table.")

            # Modify accounts to add employee_id if it doesn't exist
            await cur.execute("SHOW COLUMNS FROM accounts LIKE 'employee_id'")
            has_emp = await cur.fetchone()
            if not has_emp:
                await cur.execute("ALTER TABLE accounts ADD COLUMN employee_id CHAR(36) NULL")
                await cur.execute("ALTER TABLE accounts ADD CONSTRAINT fk_accounts_employee FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE")
                print("Added 'employee_id' column to 'accounts'.")

            # Make user_id nullable if it's NOT NULL
            await cur.execute("ALTER TABLE accounts MODIFY user_id CHAR(36) NULL")
            
            # 2. Find matching accounts
            format_strings = ','.join(['%s'] * len(ROLES_TO_MIGRATE))
            await cur.execute(f"""
                SELECT a.account_id, a.user_id, r.name as role_name 
                FROM accounts a
                JOIN roles r ON a.role_id = r.id
                WHERE r.name IN ({format_strings}) AND a.user_id IS NOT NULL
            """, tuple(ROLES_TO_MIGRATE))
            
            accounts = await cur.fetchall()
            print(f"Found {len(accounts)} accounts to migrate.")
            
            counters = {}
            for row in accounts:
                acct_id = row['account_id']
                user_id = row['user_id']
                role_name = row['role_name']
                
                # Fetch user details
                await cur.execute("SELECT * FROM user_details WHERE user_id=%s", (user_id,))
                ud = await cur.fetchone()
                if not ud:
                    print(f"Skipping account {acct_id} as no user_details found.")
                    continue
                
                # Generate new Employee ID format (NT + Role First 2 letters + # + index)
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
                
                # Insert into employees
                await cur.execute("""
                    INSERT INTO employees 
                    (employee_id, employee_id_number, name, address, email, contact_number, first_name, last_name, address_line_1, address_line_2, city, state, pincode, emergency_contact_name, emergency_contact_number, id_proof_url, onboard_date, end_date, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    emp_id, emp_id_num, ud['name'], ud['address'], ud['email'], ud['contact_number'], 
                    ud['first_name'], ud['last_name'], ud['address_line_1'], ud['address_line_2'], 
                    ud['city'], ud['state'], ud['pincode'], ud['emergency_contact_name'], 
                    ud['emergency_contact_number'], ud['id_proof_url'], ud['onboard_date'], 
                    ud['end_date'], ud['created_at']
                ))
                
                # Update accounts
                await cur.execute("UPDATE accounts SET employee_id=%s, user_id=NULL WHERE account_id=%s", (emp_id, acct_id))
                
                # We do NOT immediately delete from user_details just in case there are references, 
                # but we will delete if possible since user_id is null on accounts.
                try:
                    await cur.execute("DELETE FROM user_details WHERE user_id=%s", (user_id,))
                except Exception as e:
                    print(f"Could not delete user_details for {user_id}: {e}")
                    
                print(f"Migrated account {acct_id} to employee {emp_id_num}")

            print("Migration complete!")

    pool.close()
    await pool.wait_closed()

if __name__ == "__main__":
    asyncio.run(run_migration())
