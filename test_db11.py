import asyncio
import aiomysql

async def main():
    pool = await aiomysql.create_pool(
        host='127.0.0.1', port=3306, user='nestora', password='nestora_pass_2026', db='nestora'
    )
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("UPDATE user_details SET unit_id='19fb1622-8546-4349-a27b-f94f3ee97131' WHERE email='hardik123@nestora.com'")
            await conn.commit()
            print("Reverted Hardik's unit_id to 101 (original).")

    pool.close()
    await pool.wait_closed()

asyncio.run(main())
