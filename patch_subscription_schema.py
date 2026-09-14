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
            print("Creating subscription_plans table...")
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS subscription_plans (
                    id CHAR(36) PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    code VARCHAR(50) UNIQUE,
                    description TEXT,
                    monthly_price DECIMAL(10,2),
                    yearly_price DECIMAL(10,2),
                    trial_days INT DEFAULT 0,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            print("Creating subscription_plan_features table...")
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS subscription_plan_features (
                    id CHAR(36) PRIMARY KEY,
                    plan_id CHAR(36) NOT NULL,
                    feature_id CHAR(36) NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (plan_id) REFERENCES subscription_plans(id) ON DELETE CASCADE,
                    FOREIGN KEY (feature_id) REFERENCES features(id) ON DELETE CASCADE,
                    UNIQUE KEY unique_plan_feature (plan_id, feature_id)
                )
            """)

            print("Updating associations table...")
            try:
                await cur.execute("ALTER TABLE associations ADD COLUMN current_plan_id CHAR(36) NULL")
                await cur.execute("ALTER TABLE associations ADD FOREIGN KEY (current_plan_id) REFERENCES subscription_plans(id) ON DELETE SET NULL")
            except Exception as e:
                print(f"Skipping alter column current_plan_id: {e}")

            try:
                await cur.execute("ALTER TABLE associations ADD COLUMN subscription_start DATE NULL")
            except Exception as e:
                print(f"Skipping alter column subscription_start: {e}")

            try:
                await cur.execute("ALTER TABLE associations ADD COLUMN subscription_end DATE NULL")
            except Exception as e:
                print(f"Skipping alter column subscription_end: {e}")

            try:
                await cur.execute("ALTER TABLE associations ADD COLUMN payment_status VARCHAR(50) NULL")
            except Exception as e:
                print(f"Skipping alter column payment_status: {e}")

            try:
                await cur.execute("ALTER TABLE associations ADD COLUMN renewal_date DATE NULL")
            except Exception as e:
                print(f"Skipping alter column renewal_date: {e}")

            try:
                await cur.execute("ALTER TABLE associations ADD COLUMN subscription_status VARCHAR(50) NULL")
            except Exception as e:
                print(f"Skipping alter column subscription_status: {e}")

            print("Database setup complete!")

if __name__ == "__main__":
    asyncio.run(run_setup())
