import asyncio
from dotenv import load_dotenv
load_dotenv()
from server import init_pool, db_execute

async def main():
    await init_pool()
    try:
        await db_execute("""
        ALTER TABLE amenity_bookings 
        ADD COLUMN contact_number VARCHAR(20) DEFAULT NULL,
        ADD COLUMN unit_id CHAR(36) DEFAULT NULL,
        ADD COLUMN unit_address TEXT DEFAULT NULL;
        """)
        print("Columns added successfully!")
    except Exception as e:
        print("Error or already exists:", e)

asyncio.run(main())
