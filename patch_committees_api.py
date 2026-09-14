import os

CODE_TO_ADD = """
class CommitteeMemberIn(BaseModel):
    user_id: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class CommitteeIn(BaseModel):
    association_id: str
    name: str
    description: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    members: List[CommitteeMemberIn] = []

@api_router.get("/admin/homeowners")
async def get_homeowners(assoc_id: Optional[str] = None, account: dict = Depends(require_admin)):
    sql = '''
        SELECT a.account_id, a.user_id, a.email, ud.name, ud.profile_pic_url
        FROM accounts a
        JOIN roles r ON a.role_id = r.id
        JOIN user_details ud ON a.user_id = ud.user_id
        WHERE r.name = 'Homeowner'
    '''
    params = []
    rows = await db_fetchall(sql, tuple(params))
    return {"ok": True, "data": rows}

@api_router.get("/admin/committees")
async def get_committees(assoc_id: Optional[str] = None, account: dict = Depends(require_admin)):
    sql = '''
        SELECT c.*, a.name as association_name,
               (SELECT COUNT(*) FROM committee_members cm WHERE cm.committee_id = c.id) as member_count
        FROM committees c
        JOIN associations a ON c.association_id = a.id
    '''
    params = []
    if assoc_id and assoc_id != 'ALL':
        sql += " WHERE c.association_id = %s"
        params.append(assoc_id)
    sql += " ORDER BY c.created_at DESC"
    
    rows = await db_fetchall(sql, tuple(params))
    
    for row in rows:
        members_sql = '''
            SELECT cm.id, cm.user_id, cm.start_date, cm.end_date, ud.name, ud.profile_pic_url, a.email
            FROM committee_members cm
            JOIN user_details ud ON cm.user_id = ud.user_id
            JOIN accounts a ON ud.user_id = a.user_id
            WHERE cm.committee_id = %s
        '''
        members = await db_fetchall(members_sql, (row['id'],))
        unique_members = {m['user_id']: m for m in members}.values()
        row['members'] = list(unique_members)
        if row.get('start_date'): row['start_date'] = str(row['start_date'])
        if row.get('end_date'): row['end_date'] = str(row['end_date'])
        if row.get('created_at'): row['created_at'] = str(row['created_at'])
        for m in row['members']:
            if m.get('start_date'): m['start_date'] = str(m['start_date'])
            if m.get('end_date'): m['end_date'] = str(m['end_date'])
            
    return {"ok": True, "data": rows}

@api_router.post("/admin/committees")
async def create_committee(payload: CommitteeIn, account: dict = Depends(require_admin)):
    import uuid
    start = payload.start_date if payload.start_date else None
    end = payload.end_date if payload.end_date else None
    
    committee_id = str(uuid.uuid4())
    await db_execute(
        "INSERT INTO committees (id, association_id, name, description, start_date, end_date) VALUES (%s, %s, %s, %s, %s, %s)",
        (committee_id, payload.association_id, payload.name, payload.description, start, end)
    )
    
    cm_role = await db_fetchone("SELECT id FROM roles WHERE name='Committee member'")
    
    for member in payload.members:
        cm_id = str(uuid.uuid4())
        m_start = member.start_date if member.start_date else None
        m_end = member.end_date if member.end_date else None
        await db_execute(
            "INSERT INTO committee_members (id, committee_id, user_id, start_date, end_date) VALUES (%s, %s, %s, %s, %s)",
            (cm_id, committee_id, member.user_id, m_start, m_end)
        )
        if cm_role:
            await db_execute("UPDATE accounts SET role_id=%s WHERE user_id=%s", (cm_role["id"], member.user_id))
            
    return {"ok": True, "data": {"id": committee_id}}

@api_router.put("/admin/committees/{committee_id}")
async def update_committee(committee_id: str, payload: CommitteeIn, account: dict = Depends(require_admin)):
    import uuid
    start = payload.start_date if payload.start_date else None
    end = payload.end_date if payload.end_date else None
    
    await db_execute(
        "UPDATE committees SET association_id=%s, name=%s, description=%s, start_date=%s, end_date=%s WHERE id=%s",
        (payload.association_id, payload.name, payload.description, start, end, committee_id)
    )
    
    old_members_rows = await db_fetchall("SELECT user_id FROM committee_members WHERE committee_id=%s", (committee_id,))
    old_user_ids = [r['user_id'] for r in old_members_rows]
    new_user_ids = [m.user_id for m in payload.members]
    
    cm_role = await db_fetchone("SELECT id FROM roles WHERE name='Committee member'")
    ho_role = await db_fetchone("SELECT id FROM roles WHERE name='Homeowner'")
    
    for old_user in old_user_ids:
        if old_user not in new_user_ids:
            await db_execute("DELETE FROM committee_members WHERE committee_id=%s AND user_id=%s", (committee_id, old_user))
            if ho_role:
                await db_execute("UPDATE accounts SET role_id=%s WHERE user_id=%s", (ho_role["id"], old_user))
                
    for member in payload.members:
        m_start = member.start_date if member.start_date else None
        m_end = member.end_date if member.end_date else None
        if member.user_id in old_user_ids:
            await db_execute(
                "UPDATE committee_members SET start_date=%s, end_date=%s WHERE committee_id=%s AND user_id=%s",
                (m_start, m_end, committee_id, member.user_id)
            )
        else:
            cm_id = str(uuid.uuid4())
            await db_execute(
                "INSERT INTO committee_members (id, committee_id, user_id, start_date, end_date) VALUES (%s, %s, %s, %s, %s)",
                (cm_id, committee_id, member.user_id, m_start, m_end)
            )
            if cm_role:
                await db_execute("UPDATE accounts SET role_id=%s WHERE user_id=%s", (cm_role["id"], member.user_id))
                
    return {"ok": True}

@api_router.delete("/admin/committees/{committee_id}")
async def delete_committee(committee_id: str, account: dict = Depends(require_admin)):
    ho_role = await db_fetchone("SELECT id FROM roles WHERE name='Homeowner'")
    old_members_rows = await db_fetchall("SELECT user_id FROM committee_members WHERE committee_id=%s", (committee_id,))
    
    if ho_role:
        for r in old_members_rows:
            await db_execute("UPDATE accounts SET role_id=%s WHERE user_id=%s", (ho_role["id"], r['user_id']))
            
    await db_execute("DELETE FROM committees WHERE id=%s", (committee_id,))
    return {"ok": True}
"""

with open("server.py", "r") as f:
    content = f.read()
    
# Insert before app.include_router(api_router)
target = "app.include_router(api_router)"
if target in content and "def create_committee" not in content:
    content = content.replace(target, CODE_TO_ADD + "\n" + target)
    with open("server.py", "w") as f:
        f.write(content)
    print("Patched server.py successfully!")
else:
    print("Could not patch server.py or already patched.")
