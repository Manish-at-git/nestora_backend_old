import asyncio
import pymysql
import os
import uuid
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
        # Get all accounts
        cursor.execute("SELECT account_id FROM accounts")
        accounts = cursor.fetchall()
        
        created = 0
        for acc in accounts:
            acc_id = acc["account_id"]
            # Check if wallet exists
            cursor.execute("SELECT id FROM wallets WHERE account_id = %s", (acc_id,))
            if not cursor.fetchone():
                w_id = str(uuid.uuid4())
                cursor.execute("INSERT INTO wallets (id, account_id, balance, reward_points) VALUES (%s, %s, 0, 0)", (w_id, acc_id))
                created += 1
        print(f"Created {created} wallets.")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    asyncio.run(main())
