import asyncio
import aiomysql
import os
import bcrypt
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
DB_USER = os.getenv("MYSQL_USER", "nestora")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "nestora_pass_2026")
DB_NAME = os.getenv("MYSQL_DB", "nestora")
DB_PORT = int(os.getenv("MYSQL_PORT", 3306))

def hash_password(plain_text_password: str) -> str:
    return bcrypt.hashpw(plain_text_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

async def fix_passwords():
    pool = await aiomysql.create_pool(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, db=DB_NAME, port=DB_PORT, autocommit=True
    )
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            # Get all accounts where password hash doesn't start with $2b$
            await cur.execute("SELECT account_id FROM accounts WHERE password_hash NOT LIKE '$2b$%'")
            rows = await cur.fetchall()
            print(f"Found {len(rows)} accounts with invalid bcrypt hashes.")
            
            hashed = hash_password("nestora123")
            for r in rows:
                await cur.execute(
                    "UPDATE accounts SET password_hash = %s WHERE account_id = %s",
                    (hashed, r['account_id'])
                )
            print("Fixed passwords.")

if __name__ == "__main__":
    asyncio.run(fix_passwords())
