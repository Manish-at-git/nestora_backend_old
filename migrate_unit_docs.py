import asyncio
import os
from dotenv import load_dotenv
import aiomysql

load_dotenv('.env')

async def main():
    pool = await aiomysql.create_pool(
        host=os.environ["MYSQL_HOST"],
        port=int(os.environ["MYSQL_PORT"]),
        user=os.environ["MYSQL_USER"],
        password=os.environ["MYSQL_PASSWORD"],
        db=os.environ["MYSQL_DB"],
        autocommit=True,
    )
    
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            try:
                print("Adding unit_id column to unit_documents...")
                await cur.execute("ALTER TABLE unit_documents ADD COLUMN unit_id CHAR(36) AFTER association_id;")
                print("Column added.")
            except Exception as e:
                print("Column may already exist:", e)
                
            try:
                print("Adding foreign key constraint...")
                await cur.execute("ALTER TABLE unit_documents ADD CONSTRAINT fk_unit_doc_unit FOREIGN KEY (unit_id) REFERENCES units(id) ON DELETE CASCADE;")
                print("Foreign key added.")
            except Exception as e:
                print("FK may already exist:", e)
                
            # Let's verify the schema
            await cur.execute("DESCRIBE unit_documents;")
            result = await cur.fetchall()
            print("Current Schema:")
            for row in result:
                print(row)
                
    pool.close()
    await pool.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
