import asyncio
import aiomysql
import os
import uuid
import hashlib
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
DB_USER = os.getenv("MYSQL_USER", "nestora")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "nestora_pass_2026")
DB_NAME = os.getenv("MYSQL_DB", "nestora")
DB_PORT = int(os.getenv("MYSQL_PORT", 3306))

def hash_pass(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

async def run_seed():
    pool = await aiomysql.create_pool(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, db=DB_NAME, port=DB_PORT, autocommit=True
    )
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            # 1. Create Association
            assoc_id = str(uuid.uuid4())
            await cur.execute(
                "INSERT INTO associations (id, name, association_code, city) VALUES (%s, %s, %s, %s)",
                (assoc_id, "Demo Association", "DEMO", "Test City")
            )
            print(f"Created Association: Demo Association (ID: {assoc_id})")

            # 2. Create Block
            block_id = str(uuid.uuid4())
            await cur.execute(
                "INSERT INTO blocks (id, association_id, name) VALUES (%s, %s, %s)",
                (block_id, assoc_id, "Block A")
            )

            # 3. Create Units & Homeowners
            unit_homeowner_counts = [1, 2, 3, 4, 2]
            
            # Fetch Homeowner Role ID
            await cur.execute("SELECT id FROM roles WHERE name = 'Homeowner'")
            role_row = await cur.fetchone()
            ho_role_id = role_row['id'] if role_row else None

            created_homeowners = []
            
            for i, count in enumerate(unit_homeowner_counts):
                unit_num = f"10{i+1}"
                unit_id = str(uuid.uuid4())
                await cur.execute(
                    "INSERT INTO units (id, block_id, unit_number) VALUES (%s, %s, %s)",
                    (unit_id, block_id, unit_num)
                )
                
                for j in range(count):
                    ho_email = f"homeowner_{unit_num}_{j+1}@nestora.io"
                    ho_pass = "nestora123"
                    ho_name = f"Homeowner {j+1} (Unit {unit_num})"
                    
                    user_id = str(uuid.uuid4())
                    account_id = str(uuid.uuid4())
                    
                    # Create code request to satisfy any constraints if necessary, or just create user_details
                    code_id = str(uuid.uuid4())
                    await cur.execute("INSERT INTO user_codes (id, login_code, status) VALUES (%s, %s, %s)", (code_id, f"DEMO-{unit_num}-{j}-{str(uuid.uuid4())[:8]}", "used"))
                    
                    await cur.execute(
                        "INSERT INTO user_details (user_id, code_id, name, email, unit_id, address, contact_number) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        (user_id, code_id, ho_name, ho_email, unit_id, '123 Demo St', '555-0100')
                    )
                    
                    await cur.execute(
                        "INSERT INTO accounts (account_id, user_id, email, password_hash, role_id) VALUES (%s, %s, %s, %s, %s)",
                        (account_id, user_id, ho_email, hash_pass(ho_pass), ho_role_id)
                    )
                    created_homeowners.append((ho_email, ho_pass, unit_num))
            
            # Fetch Admin role id
            await cur.execute("SELECT id FROM roles WHERE name = 'Admin'")
            admin_role = await cur.fetchone()
            
            print("\n--- CREDENTIALS ---")
            print("Super Admin:")
            print("Email: superadmin@nestora.io")
            print("Password: nestora123")
            
            print("\nAdmin:")
            print("Email: admin@nestora.io")
            print("Password: nestora123")
            
            print("\nBoard Member:")
            print("Email: boardmember@nestora.io")
            print("Password: nestora123")
            
            print("\nHomeowners in Demo Association:")
            for ho in created_homeowners:
                print(f"Unit {ho[2]}: {ho[0]} / {ho[1]}")

if __name__ == "__main__":
    asyncio.run(run_seed())
