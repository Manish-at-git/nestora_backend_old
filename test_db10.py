import asyncio
import aiomysql

async def main():
    pool = await aiomysql.create_pool(
        host='127.0.0.1', port=3306, user='nestora', password='nestora_pass_2026', db='nestora'
    )
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("UPDATE user_details SET unit_id='09b53890-771a-4ced-884a-a6a7d2c2fc64' WHERE email='hardik123@nestora.com'")
            await conn.commit()
            print("Updated Hardik's unit_id to match Jagruti's unit_id (901).")

    pool.close()
    await pool.wait_closed()

asyncio.run(main())
