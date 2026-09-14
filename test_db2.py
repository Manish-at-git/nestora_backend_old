import asyncio
import aiomysql

async def main():
    pool = await aiomysql.create_pool(
        host='127.0.0.1', port=3306, user='nestora', password='nestora_pass_2026', db='nestora'
    )
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT id, user_id FROM unit_documents")
            docs = await cur.fetchall()
            for doc in docs:
                await cur.execute("SELECT name, email, unit_id, role_id FROM user_details WHERE user_id=%s", (doc['user_id'],))
                ud = await cur.fetchone()
                print(f"Doc {doc['id']} User {doc['user_id']} -> user_details: {ud}")

    pool.close()
    await pool.wait_closed()

asyncio.run(main())
