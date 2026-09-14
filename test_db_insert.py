import asyncio
import os
from dotenv import load_dotenv
import aiomysql
import uuid

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
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM accounts LIMIT 1;")
            account = await cur.fetchone()
            
            await cur.execute("SELECT id FROM associations LIMIT 1;")
            association = await cur.fetchone()
            assoc_id = association['id'] if association else None
            
            # The query that db_execute builds:
            # sql = sql.replace(f"({cols})", f"(id, {cols})", 1)
            # sql = sql.replace(f"({vals})", f"(%s, {vals})", 1)
            # params = (new_id,) + tuple(params)
            
            # Since we fixed server.py, let's simulate the FIXED query:
            sql = """
                INSERT INTO unit_documents (
                    association_id, user_id, name, type, description,
                    file_url, file_name, file_type, file_size_kb
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                assoc_id, account["account_id"], "Test Doc", "Unit Plan", "desc",
                "http://test", "test.pdf", "PDF", 100
            )
            
            # What db_execute actually does to this SQL:
            is_insert = sql.strip().upper().startswith("INSERT INTO")
            new_id = str(uuid.uuid4())
            import re
            pk_map = {
                'accounts': 'account_id',
                'user_details': 'user_id',
                'employees': 'employee_id',
                'code_requests': 'request_id',
                'update_requests': 'request_id',
                'admin_associations': None,
                'event_likes': None,
                'poll_likes': None,
                'poll_votes': None
            }
            
            match = re.search(r'INSERT INTO\s+([a-zA-Z0-9_]+)\s*\(([^)]+)\)\s*VALUES\s*\(([^)]+)\)', sql, re.IGNORECASE)
            if match:
                table = match.group(1).lower()
                cols = match.group(2)
                vals = match.group(3)
                pk = pk_map.get(table, 'id')
                if pk:
                    sql = sql.replace(f"({cols})", f"({pk}, {cols})", 1)
                    sql = sql.replace(f"({vals})", f"(%s, {vals})", 1)
                    params = (new_id,) + tuple(params)
                else:
                    new_id = None
            
            print("Executing SQL:", sql)
            print("With params:", params)
            
            try:
                await cur.execute(sql, params)
                print("Insert successful!")
            except Exception as e:
                print("DB Error:", e)
                
    pool.close()
    await pool.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
