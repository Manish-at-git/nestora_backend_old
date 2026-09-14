import asyncio
import aiomysql
import os
from dotenv import load_dotenv

load_dotenv()

async def check():
    pool = await aiomysql.create_pool(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"), 
        user=os.getenv("MYSQL_USER", "nestora"), 
        password=os.getenv("MYSQL_PASSWORD", "nestora_pass_2026"), 
        db=os.getenv("MYSQL_DB", "nestora"), 
        port=int(os.getenv("MYSQL_PORT", 3306))
    )
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT id, name, description FROM features")
            rows = await cur.fetchall()
            print("Features in DB:")
            for r in rows:
                print(r['name'])

asyncio.run(check())
