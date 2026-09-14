import requests

try:
    res = requests.post("http://localhost:8000/api/auth/login", json={"email": "hardik@opsistechnology.com", "password": "password"})
    token = res.json()["access_token"]
    
    res = requests.get("http://localhost:8000/api/admin/board-members", headers={"Authorization": f"Bearer {token}"})
    print("GET /admin/board-members:", res.status_code, res.text)
except Exception as e:
    print(e)
