import asyncio
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    conn = pymysql.connect(
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        db=os.getenv("MYSQL_DB"),
        autocommit=True
    )
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        # Delete wallets for accounts that have user_id IS NULL
        cursor.execute("""
            DELETE w FROM wallets w
            JOIN accounts a ON w.account_id = a.account_id
            WHERE a.user_id IS NULL
        """)
        print(f"Deleted wallets for admin/employee accounts. Rows affected: {cursor.rowcount}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    asyncio.run(main())
