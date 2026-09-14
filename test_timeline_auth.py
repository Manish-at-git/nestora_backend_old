import urllib.request
import json

def login(email, password="password123"):
    req = urllib.request.Request("http://127.0.0.1:8000/api/auth/login", data=json.dumps({"email": email, "password": password}).encode(), headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read())["access_token"]
    except Exception as e:
        print(f"Login failed for {email}: {e}")
        return None

def get_timeline(token):
    req = urllib.request.Request("http://127.0.0.1:8000/api/timeline?limit=10", headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            if not data.get("ok"):
                print("Error:", data)
                return
            items = data.get("data", [])
            print(f"Count: {len(items)}")
            for i in items:
                print(f"{i.get('item_type')}: {i.get('title')} ({i.get('id')})")
    except Exception as e:
        print(f"Exception: {e}")

print("Testing hardik123@nestora.com")
token = login("hardik123@nestora.com")
if token:
    get_timeline(token)
    
print("Testing hiral123@nestora.com")
token = login("hiral123@nestora.com")
if token:
    get_timeline(token)
