import asyncio
import os
from dotenv import load_dotenv
from pathlib import Path
import aiomysql

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

async def run_alter():
    pool = await aiomysql.create_pool(
        host=os.environ["MYSQL_HOST"],
        port=int(os.environ["MYSQL_PORT"]),
        user=os.environ["MYSQL_USER"],
        password=os.environ["MYSQL_PASSWORD"],
        db=os.environ["MYSQL_DB"],
        autocommit=True
    )
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            
            print("Altering committees table...")
            try:
                await cur.execute("ALTER TABLE committees ADD COLUMN description VARCHAR(5000) NULL;")
            except Exception as e:
                print(f"Skipping committees.description: {e}")
            
            try:
                await cur.execute("ALTER TABLE committees ADD COLUMN start_date DATE NULL;")
            except Exception as e:
                print(f"Skipping committees.start_date: {e}")
                
            try:
                await cur.execute("ALTER TABLE committees ADD COLUMN end_date DATE NULL;")
            except Exception as e:
                print(f"Skipping committees.end_date: {e}")
                
            print("Altering committee_members table...")
            try:
                await cur.execute("ALTER TABLE committee_members ADD COLUMN start_date DATE NULL;")
            except Exception as e:
                print(f"Skipping committee_members.start_date: {e}")
                
            try:
                await cur.execute("ALTER TABLE committee_members ADD COLUMN end_date DATE NULL;")
            except Exception as e:
                print(f"Skipping committee_members.end_date: {e}")

            print("Inserting Committee member role...")
            try:
                import uuid
                await cur.execute("SELECT id FROM roles WHERE name='Committee member'")
                res = await cur.fetchone()
                if not res:
                    new_id = str(uuid.uuid4())
                    await cur.execute("INSERT INTO roles (id, entity_id, name, description, is_active) VALUES (%s, NULL, 'Committee member', 'Committee member role', 1)", (new_id,))
            except Exception as e:
                print(f"Failed inserting role: {e}")

            print("Done altering tables.")
            
    pool.close()
    await pool.wait_closed()

if __name__ == "__main__":
    asyncio.run(run_alter())
