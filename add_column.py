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
            try:
                await cur.execute("ALTER TABLE user_details ADD COLUMN board_member_since DATE;")
                print("Column board_member_since added.")
            except Exception as e:
                print(f"Failed or already exists: {e}")
                
            # Let's set a dummy date for one of the board members to test the UI!
            try:
                await cur.execute("UPDATE user_details ud JOIN accounts a ON ud.user_id = a.user_id JOIN roles r ON a.role_id = r.id SET ud.board_member_since = '2026-01-15' WHERE r.name = 'Board member';")
                print("Dummy date populated.")
            except Exception as e:
                print(f"Failed to set dummy date: {e}")
                
    pool.close()
    await pool.wait_closed()

asyncio.run(main())
