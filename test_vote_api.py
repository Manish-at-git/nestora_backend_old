import requests

res = requests.post("http://127.0.0.1:8000/api/auth/login", json={"email": "admin@nestora.com", "password": "password123"})
print("Login:", res.status_code, res.text)
if res.status_code == 200:
    token = res.json().get("access_token") or res.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get("http://127.0.0.1:8000/api/timeline?limit=10&offset=0", headers=headers)
    print("Timeline:", res.status_code)
    timeline = res.json()
    polls = [item for item in timeline.get("data", []) if item.get("item_type") == "poll"]
    if polls:
        poll_id = polls[0]["id"]
        res_like = requests.post(f"http://127.0.0.1:8000/api/polls/{poll_id}/like", headers=headers)
        print("Like response:", res_like.status_code, res_like.text)
        
        if polls[0].get("options"):
            opt_id = polls[0]["options"][0]["id"]
            res_vote = requests.post(f"http://127.0.0.1:8000/api/polls/{poll_id}/vote", headers=headers, json={"option_ids": [opt_id]})
            print("Vote response:", res_vote.status_code, res_vote.text)
