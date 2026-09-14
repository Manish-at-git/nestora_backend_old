import sys
sys.path.insert(0, ".")
from fastapi.testclient import TestClient
from server import app, get_account_from_token

app.dependency_overrides[get_account_from_token] = lambda: {"role": "Super admin"}

client = TestClient(app)
response = client.post("/admin/vendors", json={"name": "Test Vendor", "contact_number": "1234567890"})
print(response.status_code)
print(response.json())
