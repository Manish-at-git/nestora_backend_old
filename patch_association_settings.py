import asyncio
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    conn = pymysql.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        db=os.getenv("MYSQL_DB", "nestora"),
        autocommit=True
    )
    cursor = conn.cursor()

    try:
        # Add end_date and onboarding_date to associations if they don't exist
        try:
            cursor.execute("ALTER TABLE associations ADD COLUMN end_date DATETIME NULL;")
            print("Added end_date to associations.")
        except Exception as e:
            print("end_date might already exist:", e)

        try:
            cursor.execute("ALTER TABLE associations ADD COLUMN onboarding_date DATETIME NULL;")
            print("Added onboarding_date to associations.")
        except Exception as e:
            print("onboarding_date might already exist:", e)

        # Create assessment_rules table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS assessment_rules (
            id CHAR(36) PRIMARY KEY,
            association_id CHAR(36) NOT NULL,
            frequency VARCHAR(50),
            default_amount DECIMAL(10,2),
            due_day_of_month INT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (association_id) REFERENCES associations(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        print("Created assessment_rules table.")

        # Create fine_rules table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS fine_rules (
            id CHAR(36) PRIMARY KEY,
            association_id CHAR(36) NOT NULL,
            fine_type VARCHAR(100),
            amount DECIMAL(10,2),
            grace_period_days INT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (association_id) REFERENCES associations(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        print("Created fine_rules table.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    asyncio.run(main())
