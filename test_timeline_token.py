import asyncio
import jwt
from datetime import datetime, timedelta
import pymysql.cursors
import urllib.request
import json

SECRET_KEY = "nestora_secret_key"
ALGORITHM = "HS256"

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=1440)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def test():
    conn = pymysql.connect(host='127.0.0.1', user='nestora', password='nestora_pass_2026', db='nestora', cursorclass=pymysql.cursors.DictCursor)
    with conn.cursor() as cur:
        cur.execute("SELECT account_id, email, role_id, (SELECT name FROM roles WHERE id=role_id) as role FROM accounts WHERE email='hardik123@nestora.com'")
        hardik = cur.fetchone()
        
        cur.execute("SELECT account_id, email, role_id, (SELECT name FROM roles WHERE id=role_id) as role FROM accounts WHERE email='hiral123@nestora.com'")
        hiral = cur.fetchone()
        
    for user in [hardik, hiral]:
        token = create_access_token({"sub": user['account_id'], "role": user['role']})
        req = urllib.request.Request("http://127.0.0.1:8000/api/timeline?limit=10", headers={"Authorization": f"Bearer {token}"})
        try:
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read())
                print(f"--- Timeline for {user['email']} ---")
                if not data.get("ok"):
                    print("Error:", data)
                    continue
                items = data.get("data", [])
                print(f"Count: {len(items)}")
                for i in items:
                    print(f"{i.get('item_type')}: {i.get('title')} ({i.get('id')})")
        except Exception as e:
            print(f"Exception for {user['email']}: {e}")

asyncio.run(test())
