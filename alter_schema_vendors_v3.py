import asyncio
import aiomysql
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
DB_USER = os.getenv("MYSQL_USER", "nestora")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "nestora_pass_2026")
DB_NAME = os.getenv("MYSQL_DB", "nestora")
DB_PORT = int(os.getenv("MYSQL_PORT", 3306))

async def main():
    pool = await aiomysql.create_pool(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, db=DB_NAME, port=DB_PORT, autocommit=True
    )
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            print("Altering vendors table...")
            
            columns = [
                ("contact_details_json", "TEXT"),
                ("services_offered_json", "TEXT")
            ]
            
            for col_name, col_def in columns:
                try:
                    await cur.execute(f"ALTER TABLE vendors ADD COLUMN {col_name} {col_def}")
                    print(f"Added column {col_name}")
                except aiomysql.Error as e:
                    if e.args[0] == 1060:
                        print(f"Column {col_name} already exists.")
                    else:
                        print(f"Error adding {col_name}: {e}")
                        
            print("Done.")

if __name__ == "__main__":
    asyncio.run(main())
