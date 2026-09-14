import asyncio
import aiomysql
import os
from dotenv import load_dotenv

load_dotenv()

async def create_table():
    pool = await aiomysql.create_pool(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        db=os.getenv("MYSQL_DB", "defaultdb"),
        autocommit=True
    )
    
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            print("Creating financial_reports table...")
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS financial_reports (
                    id CHAR(36) PRIMARY KEY,
                    association_id CHAR(36) NOT NULL,
                    published_month VARCHAR(50) NOT NULL,
                    report_type VARCHAR(100) NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    file_url TEXT NOT NULL,
                    uploaded_by CHAR(36),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            print("Done.")

    pool.close()
    await pool.wait_closed()

if __name__ == "__main__":
    asyncio.run(create_table())
