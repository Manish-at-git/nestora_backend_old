import asyncio
import aiomysql

async def main():
    pool = await aiomysql.create_pool(
        host='127.0.0.1', port=3306, user='nestora', password='nestora_pass_2026', db='nestora'
    )
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM accounts WHERE email LIKE '%hardik%' OR email LIKE '%board%'")
            accs = await cur.fetchall()
            for a in accs:
                await cur.execute("SELECT name, role_id FROM roles WHERE id=%s", (a['role_id'],))
                r = await cur.fetchone()
                print(f"Account: {a['email']} | User_ID: {a['user_id']} | Role: {r['name'] if r else 'None'}")
                if a['user_id']:
                    await cur.execute("SELECT name, unit_id FROM user_details WHERE user_id=%s", (a['user_id'],))
                    ud = await cur.fetchone()
                    print(f"   -> User Details: {ud}")

    pool.close()
    await pool.wait_closed()

asyncio.run(main())
