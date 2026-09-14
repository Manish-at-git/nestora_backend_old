import asyncio
import aiomysql
import os
from dotenv import load_dotenv

load_dotenv()

async def drop_db():
    conn = await aiomysql.connect(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER", "nestora"),
        password=os.getenv("MYSQL_PASSWORD", "nestora_pass_2026"),
        autocommit=True
    )
    async with conn.cursor() as cur:
        await cur.execute("DROP DATABASE IF EXISTS nestora")
        await cur.execute("CREATE DATABASE nestora")
        print("Database nestora dropped and recreated.")

if __name__ == "__main__":
    asyncio.run(drop_db())
