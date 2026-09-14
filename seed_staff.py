import asyncio
import uuid
from database import get_db_pool

async def seed():
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # Check if any staff exist
            await cur.execute("SELECT id FROM service_staff LIMIT 1")
            if await cur.fetchone():
                print("Staff already seeded")
                return

            # Get some unit ids
            await cur.execute("SELECT id FROM units LIMIT 5")
            units = await cur.fetchall()
            
            if len(units) < 2:
                print("Not enough units to seed staff")
                return
                
            u1, u2 = units[0][0], units[1][0]
            
            # Insert Staff 1 (Cook)
            s1_id = str(uuid.uuid4())
            await cur.execute(
                """
                INSERT INTO service_staff (id, staff_code, name, mobile, category, status, police_verified, id_verified)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (s1_id, "STF-001", "Ramesh Patel", "9876543210", "Cook", "Active", True, True)
            )
            # Assignments for Cook (works at 2 flats)
            await cur.execute("INSERT INTO service_staff_assignments (id, staff_id, unit_id) VALUES (%s, %s, %s)", (str(uuid.uuid4()), s1_id, u1))
            await cur.execute("INSERT INTO service_staff_assignments (id, staff_id, unit_id) VALUES (%s, %s, %s)", (str(uuid.uuid4()), s1_id, u2))
            
            # Insert Staff 2 (Maid)
            s2_id = str(uuid.uuid4())
            await cur.execute(
                """
                INSERT INTO service_staff (id, staff_code, name, mobile, category, status, police_verified)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (s2_id, "STF-002", "Sunita Sharma", "8765432109", "Housekeeper / Maid", "Active", True)
            )
            await cur.execute("INSERT INTO service_staff_assignments (id, staff_id, unit_id) VALUES (%s, %s, %s)", (str(uuid.uuid4()), s2_id, u1))
            
            # Insert Staff 3 (Blocked)
            s3_id = str(uuid.uuid4())
            await cur.execute(
                """
                INSERT INTO service_staff (id, staff_code, name, mobile, category, status, police_verified)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (s3_id, "STF-003", "Rahul Driver", "7654321098", "Driver", "Blacklisted", False)
            )
            await cur.execute("INSERT INTO service_staff_assignments (id, staff_id, unit_id) VALUES (%s, %s, %s)", (str(uuid.uuid4()), s3_id, u2))
            
            await conn.commit()
            print("Successfully seeded service staff.")

if __name__ == "__main__":
    asyncio.run(seed())
