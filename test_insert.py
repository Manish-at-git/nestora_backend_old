import asyncio
import aiomysql
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

async def main():
    pool = await aiomysql.create_pool(
        host=os.getenv('MYSQL_HOST', '127.0.0.1'),
        port=int(os.getenv('MYSQL_PORT', 3306)),
        user=os.getenv('MYSQL_USER', 'nestora'),
        password=os.getenv('MYSQL_PASSWORD', 'nestora_pass_2026'),
        db=os.getenv('MYSQL_DB', 'nestora')
    )
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            try:
                # get a valid user
                await cur.execute("SELECT account_id FROM accounts LIMIT 1")
                acc = await cur.fetchone()
                uid = acc[0]
                
                await cur.execute("SELECT id FROM associations LIMIT 1")
                ass = await cur.fetchone()
                aid = ass[0]
                
                await cur.execute("SELECT id FROM marketplace_categories LIMIT 1")
                cat = await cur.fetchone()
                cid = cat[0]
                
                item_id = str(uuid.uuid4())
                q = '''
                    INSERT INTO marketplace_items (
                        id, association_id, user_id, category_id, title, description, price, condition_state, 
                        brand, item_age, location, contact_number, is_negotiable, status, listing_type
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                '''
                print(q)
                
                await cur.execute(q, (
                    item_id, aid, uid, cid, "Test", "Test", 10.0, "New", "Brand", "Age", "Loc", "123", True, "Active", "Sell"
                ))
                print("INSERT SUCCESS")
            except Exception as e:
                print(f"ERROR: {e}")
                
            await conn.commit()
    
    pool.close()
    await pool.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
