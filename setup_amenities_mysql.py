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
            print("Creating amenities table...")
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS amenities (
                    id CHAR(36) PRIMARY KEY,
                    association_id CHAR(36) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    charges DECIMAL(10, 2) DEFAULT 0,
                    status BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (association_id) REFERENCES associations(id) ON DELETE CASCADE
                )
            """)

            print("Creating amenity_bookings table...")
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS amenity_bookings (
                    id CHAR(36) PRIMARY KEY,
                    amenity_id CHAR(36) NOT NULL,
                    user_id CHAR(36) NOT NULL,
                    association_id CHAR(36) NOT NULL,
                    unit_number VARCHAR(50),
                    homeowner_name VARCHAR(255),
                    amount DECIMAL(10, 2) DEFAULT 0,
                    booking_date DATE NOT NULL,
                    payment_status VARCHAR(50) DEFAULT 'Pending',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (amenity_id) REFERENCES amenities(id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES accounts(account_id) ON DELETE CASCADE,
                    FOREIGN KEY (association_id) REFERENCES associations(id) ON DELETE CASCADE
                )
            """)

            print("MySQL amenities setup complete!")

if __name__ == "__main__":
    asyncio.run(run_setup())
