import asyncio
import aiomysql
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    pool = await aiomysql.create_pool(
        host=os.getenv('MYSQL_HOST', '127.0.0.1'),
        port=int(os.getenv('MYSQL_PORT', 3306)),
        user=os.getenv('MYSQL_USER', 'nestora'),
        password=os.getenv('MYSQL_PASSWORD', 'nestora_pass_2026'),
        db=os.getenv('MYSQL_DB', 'nestora')
    )
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SHOW CREATE TABLE marketplace_items")
            res = await cur.fetchone()
            print(res[1])
            
            await cur.execute("SHOW TRIGGERS")
            res = await cur.fetchall()
            for r in res:
                print(r)
    
    pool.close()
    await pool.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
