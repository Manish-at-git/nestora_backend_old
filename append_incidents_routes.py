import os

with open("server.py", "r") as f:
    content = f.read()

incident_models = """
class IncidentCreate(BaseModel):
    title: str
    category: str
    incident_type: str
    severity: str
    description: Optional[str] = None
    block: Optional[str] = None
    unit: Optional[str] = None

class IncidentInvestigationUpdate(BaseModel):
    investigation_summary: Optional[str] = None
    root_cause: Optional[str] = None
    corrective_action: Optional[str] = None
    preventive_action: Optional[str] = None
    resolution_notes: Optional[str] = None
    status: Optional[str] = None
    assigned_to: Optional[str] = None

class IncidentStatusUpdate(BaseModel):
    status: str

class IncidentCommentCreate(BaseModel):
    comment: str
"""

incident_routes = """
# ==========================================
# INCIDENT MANAGEMENT
# ==========================================

@api_router.post("/incidents")
async def create_incident(payload: IncidentCreate, account: dict = Depends(get_current_account)):
    new_id = str(uuid.uuid4())
    await db_execute(
        \"\"\"
        INSERT INTO incidents (id, title, category, incident_type, severity, description, block, unit, status, reported_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Open', %s)
        \"\"\",
        (new_id, payload.title, payload.category, payload.incident_type, payload.severity, payload.description, payload.block, payload.unit, account.get("id"))
    )
    await db_execute(
        "INSERT INTO incident_history (id, incident_id, status, changed_by) VALUES (%s, %s, %s, %s)",
        (str(uuid.uuid4()), new_id, 'Open', account.get("id"))
    )
    return {"id": new_id, "message": "Incident created successfully"}

@api_router.get("/incidents")
async def get_incidents(status: Optional[str] = None, category: Optional[str] = None, account: dict = Depends(get_current_account)):
    query = "SELECT i.*, a.email as reporter_email FROM incidents i LEFT JOIN accounts a ON i.reported_by = a.id WHERE 1=1"
    params = []
    
    if status:
        query += " AND i.status = %s"
        params.append(status)
        
    if category:
        query += " AND i.category = %s"
        params.append(category)
        
    query += " ORDER BY i.created_at DESC"
    
    incidents = await db_fetchall(query, tuple(params))
    return incidents

@api_router.get("/incidents/{incident_id}")
async def get_incident(incident_id: str, account: dict = Depends(get_current_account)):
    incident = await db_fetchone("SELECT i.*, a.email as reporter_email FROM incidents i LEFT JOIN accounts a ON i.reported_by = a.id WHERE i.id = %s", (incident_id,))
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
        
    media = await db_fetchall("SELECT * FROM incident_media WHERE incident_id = %s ORDER BY created_at DESC", (incident_id,))
    comments = await db_fetchall("SELECT c.*, a.email as user_email FROM incident_comments c LEFT JOIN accounts a ON c.user_id = a.id WHERE c.incident_id = %s ORDER BY c.created_at ASC", (incident_id,))
    history = await db_fetchall("SELECT h.*, a.email as user_email FROM incident_history h LEFT JOIN accounts a ON h.changed_by = a.id WHERE h.incident_id = %s ORDER BY h.timestamp ASC", (incident_id,))
    
    incident['media'] = media
    incident['comments'] = comments
    incident['history'] = history
    return incident

@api_router.put("/incidents/{incident_id}/status")
async def update_incident_status(incident_id: str, payload: IncidentStatusUpdate, account: dict = Depends(get_current_account)):
    incident = await db_fetchone("SELECT id, status FROM incidents WHERE id = %s", (incident_id,))
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
        
    if incident["status"] != payload.status:
        closed_at_sql = ", closed_at = CURRENT_TIMESTAMP" if payload.status == "Closed" else ""
        await db_execute(f"UPDATE incidents SET status = %s{closed_at_sql} WHERE id = %s", (payload.status, incident_id))
        await db_execute(
            "INSERT INTO incident_history (id, incident_id, status, changed_by) VALUES (%s, %s, %s, %s)",
            (str(uuid.uuid4()), incident_id, payload.status, account.get("id"))
        )
    return {"message": "Status updated successfully"}

@api_router.put("/incidents/{incident_id}/investigation")
async def update_incident_investigation(incident_id: str, payload: IncidentInvestigationUpdate, account: dict = Depends(get_current_account)):
    if account.get("role") not in ["Super admin", "Admin", "Security"]:
        raise HTTPException(status_code=403, detail="Unauthorized")
        
    await db_execute(
        \"\"\"
        UPDATE incidents SET 
            investigation_summary = COALESCE(%s, investigation_summary),
            root_cause = COALESCE(%s, root_cause),
            corrective_action = COALESCE(%s, corrective_action),
            preventive_action = COALESCE(%s, preventive_action),
            resolution_notes = COALESCE(%s, resolution_notes),
            assigned_to = COALESCE(%s, assigned_to)
        WHERE id = %s
        \"\"\",
        (payload.investigation_summary, payload.root_cause, payload.corrective_action, payload.preventive_action, payload.resolution_notes, payload.assigned_to, incident_id)
    )
    
    if payload.status:
        incident = await db_fetchone("SELECT status FROM incidents WHERE id = %s", (incident_id,))
        if incident["status"] != payload.status:
            closed_at_sql = ", closed_at = CURRENT_TIMESTAMP" if payload.status == "Closed" else ""
            await db_execute(f"UPDATE incidents SET status = %s{closed_at_sql} WHERE id = %s", (payload.status, incident_id))
            await db_execute(
                "INSERT INTO incident_history (id, incident_id, status, changed_by) VALUES (%s, %s, %s, %s)",
                (str(uuid.uuid4()), incident_id, payload.status, account.get("id"))
            )
            
    return {"message": "Investigation details updated"}

@api_router.post("/incidents/{incident_id}/comments")
async def add_incident_comment(incident_id: str, payload: IncidentCommentCreate, account: dict = Depends(get_current_account)):
    new_id = str(uuid.uuid4())
    await db_execute(
        "INSERT INTO incident_comments (id, incident_id, comment, user_id) VALUES (%s, %s, %s, %s)",
        (new_id, incident_id, payload.comment, account.get("id"))
    )
    return {"id": new_id, "message": "Comment added"}

@api_router.get("/incidents/reports/summary")
async def get_incident_summary(account: dict = Depends(get_current_account)):
    if account.get("role") not in ["Super admin", "Admin", "Security"]:
        raise HTTPException(status_code=403, detail="Unauthorized")
        
    total = await db_fetchone("SELECT COUNT(*) as c FROM incidents")
    open_count = await db_fetchone("SELECT COUNT(*) as c FROM incidents WHERE status = 'Open'")
    in_progress = await db_fetchone("SELECT COUNT(*) as c FROM incidents WHERE status IN ('Under Review', 'Assigned', 'In Progress')")
    resolved = await db_fetchone("SELECT COUNT(*) as c FROM incidents WHERE status IN ('Resolved', 'Closed')")
    
    by_category = await db_fetchall("SELECT category, COUNT(*) as count FROM incidents GROUP BY category")
    by_severity = await db_fetchall("SELECT severity, COUNT(*) as count FROM incidents GROUP BY severity")
    
    return {
        "overview": {
            "total": total["c"],
            "open": open_count["c"],
            "in_progress": in_progress["c"],
            "resolved": resolved["c"]
        },
        "by_category": by_category,
        "by_severity": by_severity
    }
"""

if "class IncidentCreate(BaseModel):" not in content:
    content = content.replace("app.include_router(api_router)", incident_models + "\n" + incident_routes + "\n\napp.include_router(api_router)")
    with open("server.py", "w") as f:
        f.write(content)
    print("Incident routes appended to server.py")
else:
    print("Incident routes already exist in server.py")
