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
            UPDATE user_details u
            JOIN units un ON u.unit_id = un.id
            JOIN blocks b ON un.block_id = b.id
            JOIN associations a ON b.association_id = a.id
            SET u.name = 'Hiral Gandharva',
                u.address = CONCAT_WS(', ', 
                CONCAT(b.name, '-', un.unit_number),
                NULLIF(a.address_line_1, ''), 
                NULLIF(a.address_line_2, ''), 
                NULLIF(a.city, ''), 
                NULLIF(a.state, ''), 
                NULLIF(a.pincode, '')
            )
            WHERE u.name LIKE '%Hiral%'
            """)
            await conn.commit()
            
            await cur.execute("SELECT name, address FROM user_details WHERE name LIKE '%Hiral%'")
            rows = await cur.fetchall()
            for r in rows:
                print(r)
    pool.close()
    await pool.wait_closed()

asyncio.run(main())
