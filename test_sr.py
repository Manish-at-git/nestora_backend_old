import requests

resp = requests.post(
    "http://localhost:8000/api/service-requests",
    json={
        "service_type": "Plumbing",
        "user_id": "f5e94b23-1c39-4d64-b040-7f2873130d0d"
    }
)
print(resp.json())
