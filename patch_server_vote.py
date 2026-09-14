with open("server.py", "r") as f:
    content = f.read()

old_vote_logic = """
@api_router.post("/polls/{poll_id}/vote")
async def vote_poll(poll_id: str, payload: PollVoteIn, account: dict = Depends(get_current_account)):
    poll = await db_fetchone("SELECT id, is_multiple_choice, status FROM polls WHERE id = %s", (poll_id,))
    if not poll:
        raise HTTPException(status_code=404, detail="Poll not found")
    if poll["status"] != "Published":
        raise HTTPException(status_code=400, detail="Poll is not active")
        
    if not poll["is_multiple_choice"] and len(payload.option_ids) > 1:
        raise HTTPException(status_code=400, detail="Multiple selection is not allowed for this poll")
"""

new_vote_logic = """
@api_router.post("/polls/{poll_id}/vote")
async def vote_poll(poll_id: str, payload: PollVoteIn, account: dict = Depends(get_current_account)):
    poll = await db_fetchone("SELECT id, is_multiple_choice, status, end_date FROM polls WHERE id = %s", (poll_id,))
    if not poll:
        raise HTTPException(status_code=404, detail="Poll not found")
    if poll["status"] != "Published":
        raise HTTPException(status_code=400, detail="Poll is not active")
        
    from datetime import datetime, timedelta
    now = datetime.now()
    if poll["end_date"]:
        if now > poll["end_date"]:
            raise HTTPException(status_code=400, detail="Poll has ended")
            
    existing_votes = await db_fetchall("SELECT option_id FROM poll_votes WHERE poll_id = %s AND account_id = %s", (poll_id, account["account_id"]))
    if existing_votes and poll["end_date"]:
        if now > poll["end_date"] - timedelta(hours=2):
            raise HTTPException(status_code=400, detail="Votes cannot be changed within 2 hours of poll end time")
        
    if not poll["is_multiple_choice"] and len(payload.option_ids) > 1:
        raise HTTPException(status_code=400, detail="Multiple selection is not allowed for this poll")
"""

if "timedelta(hours=2)" not in content:
    content = content.replace(old_vote_logic.strip(), new_vote_logic.strip())
    with open("server.py", "w") as f:
        f.write(content)
