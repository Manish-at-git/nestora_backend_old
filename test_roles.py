import requests

try:
    res = requests.get("http://localhost:8000/api/admin/roles", headers={"Authorization": "Bearer test"})
    print(res.json())
except Exception as e:
    print(e)
