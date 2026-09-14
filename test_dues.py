import requests

BASE_URL = "http://127.0.0.1:8000/api"

def test_dues():
    # Login
    r = requests.post(f"{BASE_URL}/auth/login", json={"email": "homeowner_101_1@nestora.io", "password": "nestora123"})
    if r.status_code != 200:
        print("Login failed:", r.text)
        return
    token = r.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get /auth/me
    r = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    data = r.json()
    print(data)
    account = data.get("account", {})
    print("assessment_amount:", account.get("assessment_amount"))
    print("assessment_fine:", account.get("assessment_fine"))
    print("assessment_total_due:", account.get("assessment_total_due"))
    print("assessment_paid_this_month:", account.get("assessment_paid_this_month"))
    
if __name__ == "__main__":
    test_dues()
