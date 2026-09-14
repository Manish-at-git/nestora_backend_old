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
            print("Creating vendors table...")
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS vendors (
                    id CHAR(36) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    service_type VARCHAR(150) NOT NULL,
                    contact_person VARCHAR(150),
                    email VARCHAR(150),
                    contact_number VARCHAR(50),
                    address TEXT,
                    gst_number VARCHAR(100),
                    licence_url TEXT,
                    certificate_url TEXT,
                    status VARCHAR(50) DEFAULT 'Active',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("Done.")

if __name__ == "__main__":
    asyncio.run(main())
