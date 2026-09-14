import asyncio
import aiomysql

async def main():
    pool = await aiomysql.create_pool(
        host='127.0.0.1', port=3306, user='nestora', password='nestora_pass_2026', db='nestora'
    )
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM user_details WHERE unit_id='09b53890-771a-4ced-884a-a6a7d2c2fc64'")
            users = await cur.fetchall()
            for u in users:
                await cur.execute("SELECT account_id, role, user_id FROM accounts WHERE user_id=%s", (u['user_id'],))
                acc = await cur.fetchone()
                print(f"User Name: {u['name']}, Role: {acc['role'] if acc else 'None'}, Unit_ID: {u['unit_id']}, Account_User_ID: {acc['user_id'] if acc else 'None'}")
                
            await cur.execute("SELECT id, name, unit_id, user_id FROM unit_documents WHERE unit_id='09b53890-771a-4ced-884a-a6a7d2c2fc64'")
            docs = await cur.fetchall()
            print("Unit Documents:")
            for d in docs:
                print(d)

    pool.close()
    await pool.wait_closed()

asyncio.run(main())
