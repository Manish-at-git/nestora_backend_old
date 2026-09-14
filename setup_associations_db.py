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
            # 1. Update associations table
            print("Updating associations table...")
            try:
                await cur.execute("ALTER TABLE associations ADD COLUMN association_code VARCHAR(10) NULL")
                await cur.execute("ALTER TABLE associations ADD COLUMN contract_url VARCHAR(255) NULL")
                await cur.execute("ALTER TABLE associations ADD COLUMN entity_id CHAR(36) NULL")
                await cur.execute("ALTER TABLE associations ADD COLUMN address_line_1 VARCHAR(255) NULL")
                await cur.execute("ALTER TABLE associations ADD COLUMN address_line_2 VARCHAR(255) NULL")
                await cur.execute("ALTER TABLE associations ADD COLUMN city VARCHAR(100) NULL")
                await cur.execute("ALTER TABLE associations ADD COLUMN state VARCHAR(100) NULL")
                await cur.execute("ALTER TABLE associations ADD COLUMN pincode VARCHAR(20) NULL")
                await cur.execute("ALTER TABLE associations ADD COLUMN url VARCHAR(255) NULL")
            except Exception as e:
                print(f"Skipping some alter table errors (might exist): {e}")

            # 2. Create blocks table
            print("Creating blocks table...")
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS blocks (
                    id CHAR(36) PRIMARY KEY,
                    association_id CHAR(36) NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (association_id) REFERENCES associations(id) ON DELETE CASCADE
                )
            """)

            # 3. Create units table
            print("Creating units table...")
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS units (
                    id CHAR(36) PRIMARY KEY,
                    block_id CHAR(36) NOT NULL,
                    floor VARCHAR(50) NULL,
                    unit_number VARCHAR(100) NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (block_id) REFERENCES blocks(id) ON DELETE CASCADE
                )
            """)

            # 4. Add unit_id to user_details
            print("Updating user_details table...")
            try:
                await cur.execute("ALTER TABLE user_details ADD COLUMN unit_id CHAR(36) NULL")
                await cur.execute("ALTER TABLE user_details ADD FOREIGN KEY (unit_id) REFERENCES units(id) ON DELETE SET NULL")
            except Exception as e:
                print(f"Skipping user_details alter error: {e}")

            # 5. Create committees table
            print("Creating committees table...")
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS committees (
                    id CHAR(36) PRIMARY KEY,
                    association_id CHAR(36) NOT NULL,
                    name VARCHAR(150) NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (association_id) REFERENCES associations(id) ON DELETE CASCADE
                )
            """)

            # 6. Create committee_members table
            print("Creating committee_members table...")
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS committee_members (
                    id CHAR(36) PRIMARY KEY,
                    committee_id CHAR(36) NOT NULL,
                    user_id CHAR(36) NOT NULL,
                    role VARCHAR(100) NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (committee_id) REFERENCES committees(id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES user_details(user_id) ON DELETE CASCADE
                )
            """)

            print("Database setup complete!")

if __name__ == "__main__":
    asyncio.run(run_setup())
