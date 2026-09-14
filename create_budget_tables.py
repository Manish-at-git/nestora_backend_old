import asyncio
import os
from dotenv import load_dotenv
import aiomysql

load_dotenv()

async def create_tables():
    pool = await aiomysql.create_pool(
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT")),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        db=os.getenv("MYSQL_DB"),
        autocommit=True
    )
    
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # Create association_budgets table
            await cur.execute("""
            CREATE TABLE IF NOT EXISTS association_budgets (
                id VARCHAR(36) PRIMARY KEY,
                association_id VARCHAR(36) NOT NULL,
                budget_type VARCHAR(50) NOT NULL,
                financial_year_start DATE NOT NULL,
                financial_year_end DATE NOT NULL,
                file_url VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (association_id) REFERENCES associations(id) ON DELETE CASCADE
            )
            """)
            print("Created association_budgets table.")

            # Create budget_items table
            await cur.execute("""
            CREATE TABLE IF NOT EXISTS budget_items (
                id VARCHAR(36) PRIMARY KEY,
                budget_id VARCHAR(36) NOT NULL,
                row_data JSON,
                FOREIGN KEY (budget_id) REFERENCES association_budgets(id) ON DELETE CASCADE
            )
            """)
            print("Created budget_items table.")
            
    pool.close()
    await pool.wait_closed()

if __name__ == "__main__":
    asyncio.run(create_tables())
