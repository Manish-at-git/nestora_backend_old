import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

connection = pymysql.connect(
    host=os.getenv("MYSQL_HOST", "localhost"),
    port=int(os.getenv("MYSQL_PORT", 3306)),
    user=os.getenv("MYSQL_USER", "root"),
    password=os.getenv("MYSQL_PASSWORD", ""),
    database=os.getenv("MYSQL_DB", "nestora_db"),
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True
)

def create_tables():
    with connection.cursor() as cursor:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS association_bank_accounts (
            id CHAR(36) PRIMARY KEY,
            association_id CHAR(36) NOT NULL,
            account_name VARCHAR(255) NOT NULL,
            account_holder_name VARCHAR(255) NOT NULL,
            bank_name VARCHAR(255) NOT NULL,
            account_number TEXT NOT NULL,
            ifsc_code VARCHAR(50) NOT NULL,
            branch_name VARCHAR(255),
            account_type VARCHAR(50) NOT NULL,
            currency VARCHAR(10) NOT NULL,
            upi_id VARCHAR(255),
            qr_code_url VARCHAR(255),
            gateway_provider VARCHAR(100),
            merchant_id VARCHAR(255),
            api_key TEXT,
            api_secret TEXT,
            webhook_secret TEXT,
            is_default TINYINT(1) DEFAULT 0,
            status VARCHAR(20) DEFAULT 'Active',
            created_by CHAR(36),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_by CHAR(36),
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (association_id) REFERENCES associations(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id CHAR(36) PRIMARY KEY,
            entity_name VARCHAR(100) NOT NULL,
            entity_id CHAR(36) NOT NULL,
            action VARCHAR(50) NOT NULL,
            changes JSON,
            performed_by CHAR(36),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
    print("Bank accounts and audit_logs tables created successfully.")

if __name__ == "__main__":
    create_tables()
