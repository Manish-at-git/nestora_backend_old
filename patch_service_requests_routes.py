import os

SERVER_FILE = "server.py"

with open(SERVER_FILE, "r") as f:
    content = f.read()

mount_idx = content.find("# ---------- Mount ----------")
if mount_idx == -1:
    print("Could not find '# ---------- Mount ----------'")
    exit(1)

code_to_insert = """
# ---------- Service Requests & Uploads ----------
from fastapi import File, UploadFile
import shutil
import uuid
from fastapi.staticfiles import StaticFiles

UPLOAD_DIR = ROOT_DIR / "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Mount uploads directory so they can be accessed at /uploads/filename
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

@api_router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_ext = file.filename.split(".")[-1] if "." in file.filename else "bin"
    file_name = f"{uuid.uuid4()}.{file_ext}"
    file_path = UPLOAD_DIR / file_name
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"ok": True, "url": f"/uploads/{file_name}"}

class ServiceRequestIn(BaseModel):
    service_type: str
    sub_category: Optional[str] = None
    custom_title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None

@api_router.post("/service-requests")
async def create_service_request(payload: ServiceRequestIn, account: dict = Depends(get_current_account)):
    user_id = account["account_id"]
    
    # Get association_id and unit_id for the user
    res = await db_fetchall('''
        SELECT a.id as assoc_id, u.id as unit_id
        FROM accounts acc
        LEFT JOIN user_details ud ON acc.user_id = ud.user_id
        LEFT JOIN units u ON ud.unit_id = u.id
        LEFT JOIN blocks b ON u.block_id = b.id
        LEFT JOIN associations a ON b.association_id = a.id
        WHERE acc.account_id = %s
    ''', (user_id,))
    
    if not res or not res[0]['assoc_id']:
        raise HTTPException(400, "User not mapped to any association")
        
    assoc_id = res[0]['assoc_id']
    unit_id = res[0]['unit_id']
    
    req_id = await db_execute('''
        INSERT INTO service_requests (user_id, association_id, unit_id, service_type, sub_category, custom_title, description, image_url)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ''', (user_id, assoc_id, unit_id, payload.service_type, payload.sub_category, payload.custom_title, payload.description, payload.image_url))
    
    return {"ok": True, "id": req_id}

@api_router.get("/service-requests")
async def list_service_requests(account: dict = Depends(get_current_account)):
    user_id = account["account_id"]
    role_id = account.get("role_id")
    
    query = '''
        SELECT sr.*, u.unit_number, b.name as block_name, a.name as association_name, ud.name as requestor_name
        FROM service_requests sr
        LEFT JOIN units u ON sr.unit_id = u.id
        LEFT JOIN blocks b ON u.block_id = b.id
        LEFT JOIN associations a ON sr.association_id = a.id
        LEFT JOIN accounts acc ON sr.user_id = acc.account_id
        LEFT JOIN user_details ud ON acc.user_id = ud.user_id
    '''
    
    if role_id in (1, 2, 3, 4): # Admin roles
        res = await db_fetchall("SELECT association_id FROM admin_associations WHERE admin_id = %s", (user_id,))
        if res:
            assoc_ids = [r['association_id'] for r in res]
            format_strings = ','.join(['%s'] * len(assoc_ids))
            query += f" WHERE sr.association_id IN ({format_strings}) ORDER BY sr.created_at DESC"
            rows = await db_fetchall(query, tuple(assoc_ids))
        else:
            rows = await db_fetchall(query + " ORDER BY sr.created_at DESC")
    else:
        query += " WHERE sr.user_id = %s ORDER BY sr.created_at DESC"
        rows = await db_fetchall(query, (user_id,))
        
    return {"ok": True, "data": rows}

class ServiceRequestStatusIn(BaseModel):
    status: str

@api_router.patch("/service-requests/{req_id}/status")
async def update_service_request_status(req_id: int, payload: ServiceRequestStatusIn, account: dict = Depends(get_current_account)):
    await db_execute("UPDATE service_requests SET status = %s WHERE id = %s", (payload.status, req_id))
    return {"ok": True}

class ServiceRequestMessageIn(BaseModel):
    message: Optional[str] = None
    attachment_url: Optional[str] = None

@api_router.post("/service-requests/{req_id}/messages")
async def send_message(req_id: int, payload: ServiceRequestMessageIn, account: dict = Depends(get_current_account)):
    sender_id = account["account_id"]
    msg_id = await db_execute('''
        INSERT INTO service_request_messages (service_request_id, sender_id, message, attachment_url)
        VALUES (%s, %s, %s, %s)
    ''', (req_id, sender_id, payload.message, payload.attachment_url))
    
    return {"ok": True, "id": msg_id}

@api_router.get("/service-requests/{req_id}/messages")
async def get_messages(req_id: int, account: dict = Depends(get_current_account)):
    rows = await db_fetchall('''
        SELECT m.*, a.email, a.role_id, ud.name as sender_name
        FROM service_request_messages m
        JOIN accounts a ON m.sender_id = a.account_id
        LEFT JOIN user_details ud ON a.user_id = ud.user_id
        WHERE m.service_request_id = %s
        ORDER BY m.created_at ASC
    ''', (req_id,))
    return {"ok": True, "data": rows}

"""

new_content = content[:mount_idx] + code_to_insert + content[mount_idx:]

with open(SERVER_FILE, "w") as f:
    f.write(new_content)

print("Injected service request routes successfully.")
