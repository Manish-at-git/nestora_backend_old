import asyncio
import os
from dotenv import load_dotenv
import aiomysql
import requests

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
    
    # Get a super admin token
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM accounts LIMIT 1;")
            account = await cur.fetchone()
            print("Using account:", account['email'])
            
            await cur.execute("SELECT id FROM associations LIMIT 1;")
            association = await cur.fetchone()
            assoc_id = association['id'] if association else None
            
    pool.close()
    await pool.wait_closed()
    
    if not assoc_id:
        print("No association found.")
        return

    import jwt
    import datetime
    
    payload = {
        "account_id": account['account_id'],
        "email": account['email'],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=60)
    }
    token = jwt.encode(payload, os.environ["JWT_SECRET"], algorithm="HS256")
    
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "association_id": assoc_id,
        "name": "Test Doc",
        "type": "Unit Plan",
        "description": "desc",
        "file_name": "test.pdf",
        "file_url": "http://test",
        "file_type": "PDF",
        "file_size_kb": 100
    }
    
    res = requests.post("http://localhost:8000/api/unit-documents", json=data, headers=headers)
    print("POST", res.status_code, res.text)
    
    # test with missing values
    data2 = {
        "association_id": assoc_id,
        "name": "Test Doc 2",
        "type": "Unit Plan",
        "description": "",
        "file_name": "",
        "file_url": "",
        "file_type": "",
        "file_size_kb": None
    }
    res2 = requests.post("http://localhost:8000/api/unit-documents", json=data2, headers=headers)
    print("POST2", res2.status_code, res2.text)

if __name__ == "__main__":
    asyncio.run(main())
