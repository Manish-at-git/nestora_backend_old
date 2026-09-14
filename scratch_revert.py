import asyncio
from dotenv import load_dotenv
load_dotenv()
from server import init_pool, db_execute

async def main():
    await init_pool()
    try:
        await db_execute("""
        ALTER TABLE amenity_bookings 
        DROP COLUMN contact_number,
        DROP COLUMN unit_id,
        DROP COLUMN unit_address;
        """)
        print("Columns dropped successfully!")
    except Exception as e:
        print("Error or already dropped:", e)

asyncio.run(main())
