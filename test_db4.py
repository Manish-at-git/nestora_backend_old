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
                await cur.execute("SELECT email, user_id, employee_id, role_id FROM accounts WHERE account_id=%s", (doc['user_id'],))
                acc = await cur.fetchone()
                print(f"Doc {doc['id']} Uploader (account_id) {doc['user_id']} -> accounts: {acc}")
                if acc and acc['user_id']:
                    await cur.execute("SELECT name, email, unit_id FROM user_details WHERE user_id=%s", (acc['user_id'],))
                    ud = await cur.fetchone()
                    print(f"   -> user_details mapping: {ud}")
                    if ud and ud['unit_id']:
                        await cur.execute("UPDATE unit_documents SET unit_id=%s WHERE id=%s", (ud['unit_id'], doc['id']))
                        print(f"   -> UPDATED doc with unit_id: {ud['unit_id']}")
            await conn.commit()
    pool.close()
    await pool.wait_closed()

asyncio.run(main())
