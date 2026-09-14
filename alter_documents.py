import asyncio
import os
from dotenv import load_dotenv
from pathlib import Path
import aiomysql

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

async def run_alter():
    pool = await aiomysql.create_pool(
        host=os.environ["MYSQL_HOST"],
        port=int(os.environ["MYSQL_PORT"]),
        user=os.environ["MYSQL_USER"],
        password=os.environ["MYSQL_PASSWORD"],
        db=os.environ["MYSQL_DB"],
        autocommit=True
    )
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            print("Creating documents table...")
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id CHAR(36) PRIMARY KEY,
                    association_id CHAR(36) NOT NULL,
                    title VARCHAR(100) NOT NULL,
                    document_number VARCHAR(100),
                    document_type VARCHAR(50),
                    category VARCHAR(50),
                    
                    file_name VARCHAR(255),
                    file_url VARCHAR(500),
                    file_type VARCHAR(20),
                    file_size_kb INT,
                    
                    department VARCHAR(100),
                    related_module VARCHAR(50),
                    
                    visibility VARCHAR(50),
                    allow_download BOOLEAN DEFAULT TRUE,
                    
                    issue_date DATE,
                    expiry_date DATE,
                    reminder_before_expiry_days INT,
                    
                    status VARCHAR(20) DEFAULT 'Active',
                    
                    keywords VARCHAR(255),
                    remarks VARCHAR(1000),
                    
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (association_id) REFERENCES associations(id) ON DELETE CASCADE
                )
            """)
            print("Done creating documents table.")
            
    pool.close()
    await pool.wait_closed()

if __name__ == "__main__":
    asyncio.run(run_alter())
