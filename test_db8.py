import asyncio
import aiomysql

async def main():
    pool = await aiomysql.create_pool(
        host='127.0.0.1', port=3306, user='nestora', password='nestora_pass_2026', db='nestora'
    )
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM accounts WHERE email LIKE '%hardik%'")
            accs = await cur.fetchall()
            for a in accs:
                print(f"Account Email: {a['email']}, user_id: {a.get('user_id')}, account_id: {a.get('account_id')}")
                if a.get('user_id'):
                    await cur.execute("SELECT * FROM user_details WHERE user_id=%s", (a['user_id'],))
                    ud = await cur.fetchone()
                    print(f"  -> user_details: {ud}")
                else:
                    print("  -> No user_id")
    pool.close()
    await pool.wait_closed()

asyncio.run(main())
