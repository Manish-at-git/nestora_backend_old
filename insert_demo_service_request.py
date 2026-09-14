import asyncio
import aiomysql
import os
from dotenv import load_dotenv

load_dotenv()

async def insert_demo():
    conn = await aiomysql.connect(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER", "nestora"),
        password=os.getenv("MYSQL_PASSWORD", "nestora_pass_2026"),
        db=os.getenv("MYSQL_DB", "nestora"),
        autocommit=True
    )
    async with conn.cursor(aiomysql.DictCursor) as cur:
        # Get the specific homeowner
        await cur.execute("SELECT account_id FROM accounts WHERE email='homeowner@nestora.io' LIMIT 1")
        res = await cur.fetchone()
        if not res:
            print("Homeowner not found!")
            return
        account_id = res['account_id']
        
        # Get an association
        await cur.execute("SELECT id FROM associations LIMIT 1")
        assoc = await cur.fetchone()
        if not assoc:
            # Create a dummy association if it doesn't exist
            await cur.execute("INSERT INTO associations (name) VALUES ('Test Association')")
            assoc_id = cur.lastrowid
        else:
            assoc_id = assoc['id']
            
        # Get a unit
        unit_id = None
        
        query = """
            INSERT INTO service_requests (association_id, unit_id, user_id, service_type, sub_category, description, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        await cur.execute(query, (assoc_id, unit_id, account_id, 'Plumbing', 'Repair & Leak Detection', 'My kitchen sink is leaking heavily. Need someone to fix it ASAP.', 'Pending'))
        print("Demo request inserted successfully!")

    conn.close()

if __name__ == "__main__":
    asyncio.run(insert_demo())
