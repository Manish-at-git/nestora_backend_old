import os

with open("server.py", "r") as f:
    content = f.read()

visitor_models = """
class VisitorRequestIn(BaseModel):
    mobile: str
    name: str
    visitor_type: str
    number_of_visitors: int
    vehicle_number: Optional[str] = None
    photo_url: Optional[str] = None
    id_type: Optional[str] = None
    id_number: Optional[str] = None
    unit_id: str
    purpose: str
    expected_duration: Optional[str] = None
    notes: Optional[str] = None

class VisitorCheckIn(BaseModel):
    pass_code: Optional[str] = None
"""

visitor_routes = """
# ==========================================
# VISITOR MANAGEMENT (SECURITY & RESIDENT)
# ==========================================

@api_router.get("/security/visitors/search")
async def search_visitor_by_mobile(mobile: str, account: dict = Depends(require_auth)):
    # Quick entry search
    visitor = await db_fetchone("SELECT * FROM visitors WHERE mobile = %s", (mobile,))
    if not visitor:
        raise HTTPException(status_code=404, detail="Visitor not found")
    return visitor

@api_router.get("/security/residents/search")
async def search_residents(q: str, account: dict = Depends(require_auth)):
    query = f"%{q}%"
    rows = await db_fetchall(
        \"\"\"
        SELECT ud.user_id, ud.name, ud.contact_number, un.id as unit_id, un.unit_number, b.name as block_name
        FROM user_details ud
        JOIN units un ON ud.unit_id = un.id
        JOIN blocks b ON un.block_id = b.id
        WHERE ud.name LIKE %s OR ud.contact_number LIKE %s OR un.unit_number LIKE %s
        LIMIT 20
        \"\"\",
        (query, query, query)
    )
    return {"residents": rows}

@api_router.post("/security/visitor/request")
async def request_visitor_entry(payload: VisitorRequestIn, account: dict = Depends(require_auth)):
    import uuid
    
    # 1. Ensure visitor exists
    visitor = await db_fetchone("SELECT id FROM visitors WHERE mobile = %s", (payload.mobile,))
    if not visitor:
        visitor_id = str(uuid.uuid4())
        await db_execute(
            "INSERT INTO visitors (id, name, mobile, photo_url, id_type, id_number) VALUES (%s, %s, %s, %s, %s, %s)",
            (visitor_id, payload.name, payload.mobile, payload.photo_url, payload.id_type, payload.id_number)
        )
    else:
        visitor_id = visitor["id"]
        # Update details if provided
        await db_execute(
            "UPDATE visitors SET name=%s, photo_url=COALESCE(%s, photo_url) WHERE id=%s",
            (payload.name, payload.photo_url, visitor_id)
        )

    # 2. Create Visit Request
    visit_id = str(uuid.uuid4())
    await db_execute(
        \"\"\"
        INSERT INTO visitor_visits 
        (id, visitor_id, unit_id, purpose, visitor_type, number_of_visitors, vehicle_number, notes, expected_duration, status) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'Pending')
        \"\"\",
        (visit_id, visitor_id, payload.unit_id, payload.purpose, payload.visitor_type, 
         payload.number_of_visitors, payload.vehicle_number, payload.notes, payload.expected_duration)
    )

    # 3. Notify the Resident(s) of the unit
    residents = await db_fetchall("SELECT a.id FROM accounts a JOIN user_details ud ON a.user_id = ud.user_id WHERE ud.unit_id = %s", (payload.unit_id,))
    notif_title = "New Visitor Request"
    notif_msg = f"Visitor '{payload.name}' wants to visit your flat for {payload.purpose}."
    for r in residents:
        notif_id = str(uuid.uuid4())
        await db_execute(
            "INSERT INTO notifications (id, account_id, title, message, visit_id) VALUES (%s, %s, %s, %s, %s)",
            (notif_id, r["id"], notif_title, notif_msg, visit_id)
        )
    
    return {"ok": True, "visit_id": visit_id, "message": "Request sent to resident."}

@api_router.get("/security/visitor/status/{visit_id}")
async def get_visitor_status(visit_id: str, account: dict = Depends(require_auth)):
    visit = await db_fetchone("SELECT status, pass_code FROM visitor_visits WHERE id = %s", (visit_id,))
    if not visit:
        raise HTTPException(404, "Visit not found")
    return visit

@api_router.get("/resident/visitor/pending")
async def get_pending_visitor_requests(account: dict = Depends(require_auth)):
    # Get requests for resident's unit
    user_detail = await db_fetchone("SELECT unit_id FROM user_details WHERE user_id = %s", (account["user_id"],))
    if not user_detail or not user_detail["unit_id"]:
        return {"requests": []}
        
    rows = await db_fetchall(
        \"\"\"
        SELECT v.id as visit_id, vis.name, vis.mobile, vis.photo_url, v.purpose, v.visitor_type, v.number_of_visitors, v.created_at
        FROM visitor_visits v
        JOIN visitors vis ON v.visitor_id = vis.id
        WHERE v.unit_id = %s AND v.status = 'Pending'
        ORDER BY v.created_at DESC
        \"\"\",
        (user_detail["unit_id"],)
    )
    return {"requests": rows}

@api_router.post("/resident/visitor/{visit_id}/approve")
async def approve_visitor(visit_id: str, account: dict = Depends(require_auth)):
    visit = await db_fetchone("SELECT * FROM visitor_visits WHERE id = %s AND status = 'Pending'", (visit_id,))
    if not visit:
        raise HTTPException(404, "Visit not found or already processed")
    
    # Check if resident has access
    user_detail = await db_fetchone("SELECT unit_id FROM user_details WHERE user_id = %s", (account["user_id"],))
    if visit["unit_id"] != user_detail["unit_id"]:
        raise HTTPException(403, "Not authorized to approve this visit")
        
    pass_code = f"PASS-{generate_code(4)}"
    await db_execute(
        "UPDATE visitor_visits SET status = 'Approved', pass_code = %s WHERE id = %s",
        (pass_code, visit_id)
    )
    # Mark notification as read
    await db_execute("UPDATE notifications SET is_read = 1 WHERE visit_id = %s AND account_id = %s", (visit_id, account["id"]))
    
    return {"ok": True, "pass_code": pass_code}

@api_router.post("/resident/visitor/{visit_id}/reject")
async def reject_visitor(visit_id: str, account: dict = Depends(require_auth)):
    visit = await db_fetchone("SELECT * FROM visitor_visits WHERE id = %s AND status = 'Pending'", (visit_id,))
    if not visit:
        raise HTTPException(404, "Visit not found or already processed")
    
    user_detail = await db_fetchone("SELECT unit_id FROM user_details WHERE user_id = %s", (account["user_id"],))
    if visit["unit_id"] != user_detail["unit_id"]:
        raise HTTPException(403, "Not authorized to reject this visit")
        
    await db_execute("UPDATE visitor_visits SET status = 'Denied' WHERE id = %s", (visit_id,))
    await db_execute("UPDATE notifications SET is_read = 1 WHERE visit_id = %s AND account_id = %s", (visit_id, account["id"]))
    
    return {"ok": True}
"""

if "VisitorRequestIn" not in content:
    # Insert models
    content = content.replace("class UpdateRequestPayload(BaseModel):", visitor_models + "\nclass UpdateRequestPayload(BaseModel):")
    # Insert routes
    content += "\n" + visitor_routes

    with open("server.py", "w") as f:
        f.write(content)
    print("Routes appended!")
else:
    print("Routes already exist.")
