import asyncio
import aiomysql

async def main():
    pool = await aiomysql.create_pool(
        host='127.0.0.1', port=3306, user='nestora', password='nestora_pass_2026', db='nestora'
    )
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT id, user_id FROM unit_documents WHERE unit_id IS NULL")
            docs = await cur.fetchall()
            print(f"Found {len(docs)} documents without unit_id.")
            
            for doc in docs:
                await cur.execute("SELECT unit_id FROM user_details WHERE user_id=%s", (doc['user_id'],))
                ud = await cur.fetchone()
                if ud and ud['unit_id']:
                    await cur.execute("UPDATE unit_documents SET unit_id=%s WHERE id=%s", (ud['unit_id'], doc['id']))
                    print(f"Updated document {doc['id']} with unit_id {ud['unit_id']}")
            
            await conn.commit()

    pool.close()
    await pool.wait_closed()

asyncio.run(main())
