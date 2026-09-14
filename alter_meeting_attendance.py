import asyncio
import aiomysql
from dotenv import load_dotenv
from pathlib import Path
import os

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

async def main():
    pool = await aiomysql.create_pool(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        db=os.getenv("MYSQL_DB"),
        autocommit=True
    )
    
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # Create meeting_attendance table
            await cur.execute('''
                CREATE TABLE IF NOT EXISTS meeting_attendance (
                    id VARCHAR(36) PRIMARY KEY,
                    meeting_id VARCHAR(36) NOT NULL,
                    account_id VARCHAR(36) NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_meeting_account (meeting_id, account_id),
                    FOREIGN KEY (meeting_id) REFERENCES meetings(id) ON DELETE CASCADE,
                    FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE
                )
            ''')
            print("meeting_attendance table created successfully.")
            
    pool.close()
    await pool.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
