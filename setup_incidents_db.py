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

async def create_tables():
    pool = await aiomysql.create_pool(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, db=DB_NAME, port=DB_PORT, autocommit=True
    )
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                id CHAR(36) PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                category VARCHAR(50) NOT NULL,
                incident_type VARCHAR(100) NOT NULL,
                severity ENUM('Low', 'Medium', 'High', 'Critical') NOT NULL,
                description TEXT,
                block VARCHAR(50),
                unit VARCHAR(50),
                status ENUM('Open', 'Under Review', 'Assigned', 'In Progress', 'Resolved', 'Closed') DEFAULT 'Open',
                reported_by CHAR(36),
                assigned_to VARCHAR(100),
                investigation_summary TEXT,
                root_cause TEXT,
                corrective_action TEXT,
                preventive_action TEXT,
                resolution_notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                closed_at DATETIME
            )
            """)
            print("Table 'incidents' checked/created.")

            await cur.execute("""
            CREATE TABLE IF NOT EXISTS incident_media (
                id CHAR(36) PRIMARY KEY,
                incident_id CHAR(36) NOT NULL,
                file_path VARCHAR(255) NOT NULL,
                file_type ENUM('image', 'video', 'audio', 'document') NOT NULL,
                uploaded_by CHAR(36),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (incident_id) REFERENCES incidents(id) ON DELETE CASCADE
            )
            """)
            print("Table 'incident_media' checked/created.")

            await cur.execute("""
            CREATE TABLE IF NOT EXISTS incident_comments (
                id CHAR(36) PRIMARY KEY,
                incident_id CHAR(36) NOT NULL,
                comment TEXT NOT NULL,
                user_id CHAR(36),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (incident_id) REFERENCES incidents(id) ON DELETE CASCADE
            )
            """)
            print("Table 'incident_comments' checked/created.")

            await cur.execute("""
            CREATE TABLE IF NOT EXISTS incident_history (
                id CHAR(36) PRIMARY KEY,
                incident_id CHAR(36) NOT NULL,
                status VARCHAR(50) NOT NULL,
                changed_by CHAR(36),
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (incident_id) REFERENCES incidents(id) ON DELETE CASCADE
            )
            """)
            print("Table 'incident_history' checked/created.")

    pool.close()
    await pool.wait_closed()
    print("Database setup complete.")

if __name__ == "__main__":
    asyncio.run(create_tables())
