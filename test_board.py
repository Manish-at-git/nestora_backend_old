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
            await cur.execute('''
                SELECT ac.account_id, ud.name, ac.email, ud.contact_number, ud.profile_pic_url, ud.board_member_since
                FROM accounts ac
                JOIN roles r ON ac.role_id = r.id
                JOIN user_details ud ON ac.user_id = ud.user_id
                WHERE r.name = 'Board member'
                LIMIT 1
            ''')
            rows = await cur.fetchall()
            print(rows)
                
    pool.close()
    await pool.wait_closed()

asyncio.run(main())
