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

async def run_setup():
    pool = await aiomysql.create_pool(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, db=DB_NAME, port=DB_PORT, autocommit=True
    )
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # 1. Create service_requests table
            print("Creating service_requests table...")
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS service_requests (
                    id CHAR(36) PRIMARY KEY,
                    user_id CHAR(36) NOT NULL,
                    association_id CHAR(36) NOT NULL,
                    unit_id CHAR(36) NULL,
                    sr_display_id VARCHAR(50) NULL,
                    service_type VARCHAR(100) NOT NULL,
                    sub_category VARCHAR(100) NULL,
                    custom_title VARCHAR(255) NULL,
                    description TEXT NULL,
                    image_url VARCHAR(255) NULL,
                    status VARCHAR(50) DEFAULT 'Pending',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES accounts(account_id) ON DELETE CASCADE,
                    FOREIGN KEY (association_id) REFERENCES associations(id) ON DELETE CASCADE,
                    FOREIGN KEY (unit_id) REFERENCES units(id) ON DELETE SET NULL
                )
            """)

            # 2. Create service_request_messages table
            print("Creating service_request_messages table...")
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS service_request_messages (
                    id CHAR(36) PRIMARY KEY,
                    service_request_id CHAR(36) NOT NULL,
                    sender_id CHAR(36) NOT NULL,
                    message TEXT NULL,
                    attachment_url VARCHAR(255) NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (service_request_id) REFERENCES service_requests(id) ON DELETE CASCADE,
                    FOREIGN KEY (sender_id) REFERENCES accounts(account_id) ON DELETE CASCADE
                )
            """)

            print("Database setup complete!")

if __name__ == "__main__":
    asyncio.run(run_setup())
