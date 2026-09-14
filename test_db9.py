import asyncio
import aiomysql

async def main():
    pool = await aiomysql.create_pool(
        host='127.0.0.1', port=3306, user='nestora', password='nestora_pass_2026', db='nestora'
    )
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM units WHERE id IN ('09b53890-771a-4ced-884a-a6a7d2c2fc64', '19fb1622-8546-4349-a27b-f94f3ee97131')")
            units = await cur.fetchall()
            for u in units:
                await cur.execute("SELECT name FROM blocks WHERE id=%s", (u['block_id'],))
                b = await cur.fetchone()
                print(f"Unit ID: {u['id']}, Number: {u['unit_number']}, Block: {b['name'] if b else 'None'}")

    pool.close()
    await pool.wait_closed()

asyncio.run(main())
