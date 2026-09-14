import asyncio
import aiomysql

async def main():
    pool = await aiomysql.create_pool(
        host='127.0.0.1', port=3306, user='nestora', password='nestora_pass_2026', db='nestora'
    )
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("DESCRIBE user_details;")
            res = await cur.fetchall()
            print("user_details schema:")
            for r in res:
                print(r['Field'], r['Type'])

            await cur.execute("DESCRIBE unit_documents;")
            res2 = await cur.fetchall()
            print("\nunit_documents schema:")
            for r in res2:
                print(r['Field'], r['Type'])
                
            await cur.execute("SELECT * FROM unit_documents LIMIT 5;")
            docs = await cur.fetchall()
            print("\nunit_documents rows:")
            print(docs)

    pool.close()
    await pool.wait_closed()

asyncio.run(main())
