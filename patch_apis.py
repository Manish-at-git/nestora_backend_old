import re

with open("server.py", "r") as f:
    content = f.read()

new_apis = """
@api_router.get("/admin/associations/{assoc_id}/homeowners")
async def get_assoc_homeowners(assoc_id: str, account: dict = Depends(require_admin)):
    rows = await db_fetchall('''
        SELECT a.account_id, ud.name, ud.profile_pic_url
        FROM accounts a
        JOIN roles r ON a.role_id = r.id
        JOIN user_details ud ON a.user_id = ud.user_id
        JOIN units u ON ud.unit_id = u.id
        JOIN blocks b ON u.block_id = b.id
        WHERE b.association_id = %s AND r.name = 'Homeowner'
        ORDER BY ud.name ASC
    ''', (assoc_id,))
    return {"ok": True, "data": rows}

class BoardMemberIn(BaseModel):
    association_id: str
    account_id: str
    term_start_date: str
    term_end_date: str

@api_router.post("/admin/board-members")
async def create_board_member(payload: BoardMemberIn, account: dict = Depends(require_admin)):
    import datetime
    start = datetime.datetime.strptime(payload.term_start_date, "%Y-%m-%d").date()
    end = datetime.datetime.strptime(payload.term_end_date, "%Y-%m-%d").date()
    if end < start:
        raise HTTPException(status_code=400, detail="Term end date cannot be before start date.")
        
    role = await db_fetchone("SELECT id FROM roles WHERE name='Board member'")
    
    # insert board member record
    new_id = await db_execute(
        "INSERT INTO board_members (association_id, account_id, term_start_date, term_end_date, created_by) VALUES (%s, %s, %s, %s, %s)",
        (payload.association_id, payload.account_id, start, end, account["account_id"])
    )
    
    # update account role
    await db_execute("UPDATE accounts SET role_id=%s WHERE account_id=%s", (role["id"], payload.account_id))
    
    return {"ok": True, "data": {"id": new_id}}

@api_router.get("/admin/board-members")
async def get_admin_board_members(assoc_id: Optional[str] = None, account: dict = Depends(require_admin)):
    sql = '''
        SELECT bm.id, bm.term_start_date, bm.term_end_date, bm.status, 
               a.account_id, ud.name, ud.profile_pic_url, ud.contact_number, a.email,
               assoc.name as association_name
        FROM board_members bm
        JOIN accounts a ON bm.account_id = a.account_id
        JOIN user_details ud ON a.user_id = ud.user_id
        JOIN associations assoc ON bm.association_id = assoc.id
    '''
    params = []
    if assoc_id:
        sql += " WHERE bm.association_id = %s"
        params.append(assoc_id)
        
    sql += " ORDER BY bm.created_at DESC"
    
    rows = await db_fetchall(sql, tuple(params))
    for r in rows:
        r["term_start_date"] = r["term_start_date"].isoformat() if r.get("term_start_date") else None
        r["term_end_date"] = r["term_end_date"].isoformat() if r.get("term_end_date") else None
        
    return {"ok": True, "data": rows}

@api_router.put("/admin/board-members/{bm_id}/end-term")
async def end_board_member_term(bm_id: str, account: dict = Depends(require_admin)):
    bm = await db_fetchone("SELECT account_id FROM board_members WHERE id=%s", (bm_id,))
    if not bm:
        raise HTTPException(status_code=404, detail="Board member not found")
        
    role = await db_fetchone("SELECT id FROM roles WHERE name='Homeowner'")
    
    import datetime
    now = datetime.datetime.now().date()
    
    # Set status to past and term_end_date to today
    await db_execute("UPDATE board_members SET status='past', term_end_date=%s WHERE id=%s", (now, bm_id))
    await db_execute("UPDATE accounts SET role_id=%s WHERE account_id=%s", (role["id"], bm["account_id"]))
    
    return {"ok": True}
"""

if "get_assoc_homeowners" not in content:
    content = content + "\n" + new_apis
    with open("server.py", "w") as f:
        f.write(content)
