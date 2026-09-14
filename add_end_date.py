import asyncio
import aiomysql
import os
from dotenv import load_dotenv

load_dotenv()

async def alter_db():
    conn = await aiomysql.connect(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER", "nestora"),
        password=os.getenv("MYSQL_PASSWORD", "nestora_pass_2026"),
        db=os.getenv("MYSQL_DB", "nestora"),
        autocommit=True
    )
    async with conn.cursor() as cur:
        try:
            await cur.execute("ALTER TABLE service_requests ADD COLUMN end_date DATETIME NULL")
            print("Column added successfully!")
        except Exception as e:
            print(f"Error adding column (maybe it already exists?): {e}")

if __name__ == "__main__":
    asyncio.run(alter_db())
