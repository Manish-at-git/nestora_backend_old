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
        async with conn.cursor() as cur:
            # Delete user_details that don't have an account
            await cur.execute("""
            DELETE u FROM user_details u
            LEFT JOIN accounts a ON u.user_id = a.user_id
            WHERE a.account_id IS NULL AND u.email IN ('hardik91@nestora.ai', 'hardik123@Nestora.com', 'hardik123@nestora.com')
            """)
            await conn.commit()
            print(f"Deleted duplicate rows: {cur.rowcount}")
    pool.close()
    await pool.wait_closed()

asyncio.run(main())
