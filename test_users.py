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
            SELECT 
                u.user_id, u.first_name, a.account_id, r.name as role_name
            FROM user_details u
            LEFT JOIN accounts a ON u.user_id = a.user_id
            LEFT JOIN roles r ON a.role_id = r.id
            LEFT JOIN user_codes uc ON u.code_id = uc.id
            LEFT JOIN units un ON u.unit_id = un.id
            LEFT JOIN blocks b ON un.block_id = b.id
            LEFT JOIN associations assoc ON b.association_id = assoc.id
            WHERE b.association_id IS NOT NULL
            ORDER BY u.created_at DESC
            """)
            rows = await cur.fetchall()
            for r in rows:
                print(r)
    pool.close()
    await pool.wait_closed()

asyncio.run(main())
