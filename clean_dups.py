import asyncio
import os
import aiomysql
from dotenv import load_dotenv

load_dotenv()

async def main():
    pool = await aiomysql.create_pool(
        host=os.environ["MYSQL_HOST"],
        port=int(os.environ["MYSQL_PORT"]),
        user=os.environ["MYSQL_USER"],
        password=os.environ["MYSQL_PASSWORD"],
        db=os.environ["MYSQL_DB"]
    )
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("""
            SELECT u.user_id, u.email, u.name, a.account_id, u.code_id
            FROM user_details u
            LEFT JOIN accounts a ON u.user_id = a.user_id
            WHERE u.email IN ('hardik91@nestora.ai', 'hardik123@Nestora.com')
            """)
            rows = await cur.fetchall()
            for r in rows:
                print(r)
    pool.close()
    await pool.wait_closed()

asyncio.run(main())
