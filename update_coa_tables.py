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

async def update_tables():
    pool = await aiomysql.create_pool(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, db=DB_NAME, port=DB_PORT, autocommit=True
    )
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            print("Dropping existing association_chart_of_accounts table...")
            await cur.execute("DROP TABLE IF EXISTS association_chart_of_accounts")
            print("Dropping existing global_chart_of_accounts table...")
            await cur.execute("DROP TABLE IF EXISTS global_chart_of_accounts")
            
            print("Creating global_chart_of_accounts table...")
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS global_chart_of_accounts (
                    id VARCHAR(36) PRIMARY KEY,
                    gl_code VARCHAR(255) NOT NULL,
                    gl_name VARCHAR(255) NOT NULL,
                    structure VARCHAR(255),
                    `grouping` VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("global_chart_of_accounts created.")

            print("Creating association_chart_of_accounts table...")
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS association_chart_of_accounts (
                    id VARCHAR(36) PRIMARY KEY,
                    association_id VARCHAR(36) NOT NULL,
                    gl_code VARCHAR(255) NOT NULL,
                    gl_name VARCHAR(255) NOT NULL,
                    structure VARCHAR(255),
                    `grouping` VARCHAR(255),
                    mapped_from_global_id VARCHAR(36),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (association_id) REFERENCES associations(id) ON DELETE CASCADE
                )
            """)
            print("association_chart_of_accounts created.")
    
    pool.close()
    await pool.wait_closed()

if __name__ == "__main__":
    asyncio.run(update_tables())
