import asyncio
import os
import aiomysql
from dotenv import load_dotenv

load_dotenv()

async def run():
    pool = await aiomysql.create_pool(
        host=os.environ["MYSQL_HOST"],
        port=int(os.environ["MYSQL_PORT"]),
        user=os.environ["MYSQL_USER"],
        password=os.environ["MYSQL_PASSWORD"],
        db=os.environ["MYSQL_DB"]
    )
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            try:
                await cur.execute("SELECT * FROM poll_likes LIMIT 1")
                print("poll_likes table exists")
            except Exception as e:
                print(f"Error checking poll_likes: {e}")
                
            try:
                await cur.execute("SELECT * FROM poll_comments LIMIT 1")
                print("poll_comments table exists")
            except Exception as e:
                print(f"Error checking poll_comments: {e}")
                
    pool.close()
    await pool.wait_closed()

asyncio.run(run())
