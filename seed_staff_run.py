import asyncio
import uuid
import os
import sys

# Add the current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from server import db_execute, db_fetchone, db_fetchall, app

async def seed():
    # Wait, db_execute relies on the global app state.
    # Actually, we can just use aiomysql directly.
    import aiomysql
    pool = await aiomysql.create_pool(
        host="localhost",
        port=3306,
        user="root",
        password="",
        db="nestora",
        autocommit=True
    )
    
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT id FROM service_staff LIMIT 1")
            if await cur.fetchone():
                print("Staff already seeded")
                return

            await cur.execute("SELECT id FROM units LIMIT 5")
            units = await cur.fetchall()
            if len(units) < 2:
                print("Not enough units to seed staff")
                return
                
            u1, u2 = units[0]["id"], units[1]["id"]
            
            s1_id = str(uuid.uuid4())
            await cur.execute(
                """
                INSERT INTO service_staff (id, staff_code, name, mobile, category, status, police_verified, id_verified)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (s1_id, "STF-001", "Ramesh Patel", "9876543210", "Cook", "Active", True, True)
            )
            await cur.execute("INSERT INTO service_staff_assignments (id, staff_id, unit_id) VALUES (%s, %s, %s)", (str(uuid.uuid4()), s1_id, u1))
            await cur.execute("INSERT INTO service_staff_assignments (id, staff_id, unit_id) VALUES (%s, %s, %s)", (str(uuid.uuid4()), s1_id, u2))
            
            s2_id = str(uuid.uuid4())
            await cur.execute(
                """
                INSERT INTO service_staff (id, staff_code, name, mobile, category, status, police_verified)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (s2_id, "STF-002", "Sunita Sharma", "8765432109", "Housekeeper / Maid", "Active", True)
            )
            await cur.execute("INSERT INTO service_staff_assignments (id, staff_id, unit_id) VALUES (%s, %s, %s)", (str(uuid.uuid4()), s2_id, u1))
            
            s3_id = str(uuid.uuid4())
            await cur.execute(
                """
                INSERT INTO service_staff (id, staff_code, name, mobile, category, status, police_verified)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (s3_id, "STF-003", "Rahul Driver", "7654321098", "Driver", "Blacklisted", False)
            )
            await cur.execute("INSERT INTO service_staff_assignments (id, staff_id, unit_id) VALUES (%s, %s, %s)", (str(uuid.uuid4()), s3_id, u2))
            
            print("Successfully seeded service staff.")
    
    pool.close()
    await pool.wait_closed()

if __name__ == "__main__":
    asyncio.run(seed())
