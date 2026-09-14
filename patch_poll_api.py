with open("server.py", "r") as f:
    content = f.read()

endpoints = """
@api_router.post("/polls/{poll_id}/like")
async def toggle_poll_like(poll_id: str, account: dict = Depends(get_current_account)):
    row = await db_fetchone("SELECT * FROM poll_likes WHERE poll_id = %s AND account_id = %s", (poll_id, account["account_id"]))
    if row:
        await db_execute("DELETE FROM poll_likes WHERE poll_id = %s AND account_id = %s", (poll_id, account["account_id"]))
        return {"ok": True, "liked": False}
    else:
        await db_execute("INSERT INTO poll_likes (poll_id, account_id) VALUES (%s, %s)", (poll_id, account["account_id"]))
        return {"ok": True, "liked": True}

@api_router.get("/polls/{poll_id}/comments")
async def get_poll_comments(poll_id: str, account: dict = Depends(get_current_account)):
    comments = await db_fetchall('''
        SELECT c.*, COALESCE(ud.name, e.name, a.email) as author_name
        FROM poll_comments c
        JOIN accounts a ON c.account_id = a.account_id
        LEFT JOIN user_details ud ON a.user_id = ud.user_id
        LEFT JOIN employees e ON a.employee_id = e.employee_id
        WHERE c.poll_id = %s
        ORDER BY c.created_at ASC
    ''', (poll_id,))
    for c in comments:
        c["created_at"] = c["created_at"].isoformat() if c.get("created_at") else None
    return {"ok": True, "data": comments}

class CommentIn(BaseModel):
    content: str

@api_router.post("/polls/{poll_id}/comments")
async def post_poll_comment(poll_id: str, payload: CommentIn, account: dict = Depends(get_current_account)):
    await db_execute("INSERT INTO poll_comments (poll_id, account_id, content) VALUES (%s, %s, %s)", (poll_id, account["account_id"], payload.content))
    return {"ok": True}
"""

if "toggle_poll_like" not in content:
    content = content.replace('@api_router.post("/admin/polls")', endpoints + '\n@api_router.post("/admin/polls")')
    with open("server.py", "w") as f:
        f.write(content)
    print("Patched server.py")
else:
    print("Already patched")
