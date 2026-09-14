import asyncio
import aiomysql
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    pool = await aiomysql.create_pool(
        host=os.getenv('MYSQL_HOST', '127.0.0.1'),
        port=int(os.getenv('MYSQL_PORT', 3306)),
        user=os.getenv('MYSQL_USER', 'nestora'),
        password=os.getenv('MYSQL_PASSWORD', 'nestora_pass_2026'),
        db=os.getenv('MYSQL_DB', 'nestora')
    )
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            try:
                await cur.execute("ALTER TABLE marketplace_items ADD COLUMN listing_type VARCHAR(50) DEFAULT 'Sell'")
                print("Added listing_type to marketplace_items")
            except aiomysql.Error as err:
                print(f"Error (might already exist): {err}")
                
            await conn.commit()
    
    pool.close()
    await pool.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
