import requests

try:
    res = requests.post("http://localhost:8000/api/auth/login", json={"email": "hardik@opsistechnology.com", "password": "password"})
    token = res.json()["access_token"]
    print("Token obtained")
    
    res = requests.get("http://localhost:8000/api/admin/board-members", headers={"Authorization": f"Bearer {token}"})
    print(res.status_code, res.text)
except Exception as e:
    print(e)
