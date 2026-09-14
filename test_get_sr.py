import asyncio
from server import db_fetchall

async def test():
    import aiomysql
    query = '''
        SELECT sr.*, u.unit_number, b.name as block_name, a.name as association_name, ud.name as requestor_name, ud.contact_number as requestor_phone, ac.email as requestor_email
        FROM service_requests sr
        LEFT JOIN units u ON sr.unit_id = u.id
        LEFT JOIN blocks b ON u.block_id = b.id
        LEFT JOIN associations a ON sr.association_id = a.id
        LEFT JOIN accounts ac ON sr.user_id = ac.account_id
        LEFT JOIN user_details ud ON ac.user_id = ud.user_id
    '''
    import os
    pool = await aiomysql.create_pool(
        host=os.getenv('MYSQL_HOST', '127.0.0.1'),
        port=int(os.getenv('MYSQL_PORT', 3306)),
        user=os.getenv('MYSQL_USER', 'nestora'),
        password=os.getenv('MYSQL_PASSWORD', 'nestora_pass_2026'),
        db=os.getenv('MYSQL_DB', 'nestora'),
        autocommit=True
    )
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            assoc_ids = ['5a16f53c-62e5-4945-b2eb-c73330af5cc6', '38cc8c0e-8076-45c5-b346-1debb90a8f62']
            format_strings = ','.join(['%s'] * len(assoc_ids))
            q = query + f" WHERE sr.association_id IN ({format_strings}) ORDER BY sr.created_at DESC"
            await cur.execute(q, tuple(assoc_ids))
            rows = await cur.fetchall()
            print("Returned rows:", len(rows))
            for r in rows:
                print(r['id'], r['status'])

asyncio.run(test())
