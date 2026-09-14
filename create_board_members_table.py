import asyncio
import os
import aiomysql
from dotenv import load_dotenv

load_dotenv()

async def main():
    pool = await aiomysql.create_pool(
        host=os.environ["MYSQL_HOST"],
        port=int(os.environ["MYSQL_PORT"]),
        user=os.environ["MYSQL_USER"],
        password=os.environ["MYSQL_PASSWORD"],
        db=os.environ["MYSQL_DB"]
    )
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
            CREATE TABLE IF NOT EXISTS board_members (
              id CHAR(36) PRIMARY KEY,
              association_id CHAR(36) NOT NULL,
              account_id CHAR(36) NOT NULL,
              term_start_date DATE NOT NULL,
              term_end_date DATE NOT NULL,
              status ENUM('active', 'past') DEFAULT 'active',
              created_by CHAR(36) NULL,
              created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
              FOREIGN KEY (association_id) REFERENCES associations(id) ON DELETE CASCADE,
              FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE,
              FOREIGN KEY (created_by) REFERENCES accounts(account_id) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            print("Table board_members created.")
    pool.close()
    await pool.wait_closed()

asyncio.run(main())
