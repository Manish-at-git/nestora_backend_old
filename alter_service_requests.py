import asyncio
import aiomysql
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    pool = await aiomysql.create_pool(
        host=os.getenv('MYSQL_HOST', '127.0.0.1'), 
        user=os.getenv('MYSQL_USER', 'nestora'), 
        password=os.getenv('MYSQL_PASSWORD', 'nestora_pass_2026'), 
        db=os.getenv('MYSQL_DB', 'nestora'), 
        port=int(os.getenv('MYSQL_PORT', 3306)),
        autocommit=True
    )
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("ALTER TABLE service_requests MODIFY user_id CHAR(36) NULL;")
            await cur.execute("ALTER TABLE service_requests MODIFY association_id CHAR(36) NULL;")
            print("Successfully altered service_requests table.")
            
            await cur.execute("DESCRIBE service_requests;")
            rows = await cur.fetchall()
            for r in rows:
                print(r)

if __name__ == "__main__":
    asyncio.run(main())
