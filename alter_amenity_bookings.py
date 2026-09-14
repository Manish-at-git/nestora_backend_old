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
                await cur.execute("ALTER TABLE amenity_bookings ADD COLUMN start_time TIME NULL")
                print("Added start_time")
            except Exception as e:
                print(e)
            try:
                await cur.execute("ALTER TABLE amenity_bookings ADD COLUMN end_time TIME NULL")
                print("Added end_time")
            except Exception as e:
                print(e)
            try:
                await cur.execute("ALTER TABLE amenity_bookings ADD COLUMN duration_hours INT NULL")
                print("Added duration_hours")
            except Exception as e:
                print(e)
            
            print("Done")

if __name__ == "__main__":
    asyncio.run(alter_db())
