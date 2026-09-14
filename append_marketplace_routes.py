import os

routes = """
# --- Marketplace ---

class MarketplaceItemIn(BaseModel):
    title: str
    description: Optional[str] = None
    category_id: str
    price: Optional[float] = None
    condition_state: Optional[str] = None
    brand: Optional[str] = None
    item_age: Optional[str] = None
    location: Optional[str] = None
    contact_number: Optional[str] = None
    is_negotiable: Optional[bool] = False
    status: Optional[str] = 'Active'
    images: List[str] = []

class MarketplaceItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[str] = None
    price: Optional[float] = None
    condition_state: Optional[str] = None
    brand: Optional[str] = None
    item_age: Optional[str] = None
    location: Optional[str] = None
    contact_number: Optional[str] = None
    is_negotiable: Optional[bool] = None
    status: Optional[str] = None
    images: Optional[List[str]] = None

class MarketplaceChatMessageIn(BaseModel):
    message: str

class MarketplaceReportIn(BaseModel):
    reason: str

@api_router.get("/marketplace/categories")
async def get_marketplace_categories():
    rows = await db_fetchall("SELECT * FROM marketplace_categories ORDER BY name")
    return {"ok": True, "data": rows}

@api_router.get("/marketplace/items")
async def get_marketplace_items(
    account: dict = Depends(get_current_account),
    category_id: Optional[str] = None,
    condition: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    is_negotiable: Optional[bool] = None,
    status: Optional[str] = 'Active',
    sort: Optional[str] = 'Newest'
):
    query = '''
        SELECT i.*, c.name as category_name, 
               COALESCE(ud.name, emp.name, acc.email) as seller_name,
               (SELECT COUNT(*) FROM marketplace_favorites f WHERE f.item_id = i.id AND f.user_id = %s) as is_saved,
               (SELECT COUNT(*) FROM marketplace_favorites f WHERE f.item_id = i.id) as saves_count
        FROM marketplace_items i
        LEFT JOIN marketplace_categories c ON i.category_id = c.id
        LEFT JOIN accounts acc ON i.user_id = acc.account_id
        LEFT JOIN user_details ud ON acc.user_id = ud.user_id
        LEFT JOIN employees emp ON acc.employee_id = emp.employee_id
        WHERE 1=1
    '''
    params = [account["account_id"]]
    
    if status:
        query += " AND i.status = %s"
        params.append(status)
    if category_id:
        query += " AND i.category_id = %s"
        params.append(category_id)
    if condition:
        query += " AND i.condition_state = %s"
        params.append(condition)
    if min_price is not None:
        query += " AND i.price >= %s"
        params.append(min_price)
    if max_price is not None:
        query += " AND i.price <= %s"
        params.append(max_price)
    if is_negotiable is not None:
        query += " AND i.is_negotiable = %s"
        params.append(is_negotiable)
        
    if sort == 'Oldest':
        query += " ORDER BY i.created_at ASC"
    else:
        query += " ORDER BY i.created_at DESC"
        
    items = await db_fetchall(query, tuple(params))
    
    # Fetch images for all items
    if items:
        item_ids = [str(item['id']) for item in items]
        placeholders = ','.join(['%s'] * len(item_ids))
        img_query = f"SELECT item_id, image_url FROM marketplace_images WHERE item_id IN ({placeholders})"
        images = await db_fetchall(img_query, tuple(item_ids))
        
        img_map = {}
        for img in images:
            img_map.setdefault(img['item_id'], []).append(img['image_url'])
            
        for item in items:
            item['images'] = img_map.get(item['id'], [])
            if item.get('created_at'): item['created_at'] = str(item['created_at'])
            if item.get('updated_at'): item['updated_at'] = str(item['updated_at'])
            
    return {"ok": True, "data": items}

@api_router.get("/marketplace/items/my")
async def get_my_marketplace_items(account: dict = Depends(get_current_account)):
    query = '''
        SELECT i.*, c.name as category_name,
               (SELECT COUNT(*) FROM marketplace_favorites f WHERE f.item_id = i.id) as saves_count
        FROM marketplace_items i
        LEFT JOIN marketplace_categories c ON i.category_id = c.id
        WHERE i.user_id = %s
        ORDER BY i.created_at DESC
    '''
    items = await db_fetchall(query, (account["account_id"],))
    
    if items:
        item_ids = [str(item['id']) for item in items]
        placeholders = ','.join(['%s'] * len(item_ids))
        img_query = f"SELECT item_id, image_url FROM marketplace_images WHERE item_id IN ({placeholders})"
        images = await db_fetchall(img_query, tuple(item_ids))
        
        img_map = {}
        for img in images:
            img_map.setdefault(img['item_id'], []).append(img['image_url'])
            
        for item in items:
            item['images'] = img_map.get(item['id'], [])
            if item.get('created_at'): item['created_at'] = str(item['created_at'])
            if item.get('updated_at'): item['updated_at'] = str(item['updated_at'])
            
    return {"ok": True, "data": items}

@api_router.post("/marketplace/items")
async def create_marketplace_item(payload: MarketplaceItemIn, account: dict = Depends(get_current_account)):
    # Get association_id for the user
    assoc_id = None
    if account.get("user_id"):
        ud_row = await db_fetchone("SELECT ud.unit_id, u.block_id, b.association_id FROM user_details ud LEFT JOIN units u ON ud.unit_id=u.id LEFT JOIN blocks b ON u.block_id=b.id WHERE ud.user_id=%s", (account["user_id"],))
        if ud_row:
            assoc_id = ud_row.get("association_id")
    elif account.get("employee_id"):
        emp_row = await db_fetchone("SELECT association_id FROM employees WHERE employee_id=%s", (account["employee_id"],))
        if emp_row:
            assoc_id = emp_row.get("association_id")
            
    if not assoc_id:
        assoc_id = "00000000-0000-0000-0000-000000000000" # Fallback if no association found (Admins might not have one)
        
    item_id = str(uuid.uuid4())
    await db_execute('''
        INSERT INTO marketplace_items (
            id, association_id, user_id, category_id, title, description, price, condition_state, 
            brand, item_age, location, contact_number, is_negotiable, status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (
        item_id, assoc_id, account["account_id"], payload.category_id, payload.title, payload.description,
        payload.price, payload.condition_state, payload.brand, payload.item_age, payload.location,
        payload.contact_number, payload.is_negotiable, payload.status
    ))
    
    for img_url in payload.images:
        await db_execute("INSERT INTO marketplace_images (id, item_id, image_url) VALUES (%s, %s, %s)", (str(uuid.uuid4()), item_id, img_url))
        
    return {"ok": True, "id": item_id}

@api_router.put("/marketplace/items/{item_id}")
async def update_marketplace_item(item_id: str, payload: MarketplaceItemUpdate, account: dict = Depends(get_current_account)):
    item = await db_fetchone("SELECT user_id FROM marketplace_items WHERE id=%s", (item_id,))
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    if item['user_id'] != account["account_id"] and account["role"] not in ["Super admin", "Admin"]:
        raise HTTPException(status_code=403, detail="Forbidden")
        
    updates = []
    params = []
    for k, v in payload.dict(exclude_unset=True).items():
        if k != "images":
            updates.append(f"{k}=%s")
            params.append(v)
            
    if updates:
        params.append(item_id)
        query = f"UPDATE marketplace_items SET {', '.join(updates)} WHERE id=%s"
        await db_execute(query, tuple(params))
        
    if payload.images is not None:
        await db_execute("DELETE FROM marketplace_images WHERE item_id=%s", (item_id,))
        for img_url in payload.images:
            await db_execute("INSERT INTO marketplace_images (id, item_id, image_url) VALUES (%s, %s, %s)", (str(uuid.uuid4()), item_id, img_url))
            
    return {"ok": True}

@api_router.delete("/marketplace/items/{item_id}")
async def delete_marketplace_item(item_id: str, account: dict = Depends(get_current_account)):
    item = await db_fetchone("SELECT user_id FROM marketplace_items WHERE id=%s", (item_id,))
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    if item['user_id'] != account["account_id"] and account["role"] not in ["Super admin", "Admin"]:
        raise HTTPException(status_code=403, detail="Forbidden")
        
    await db_execute("DELETE FROM marketplace_items WHERE id=%s", (item_id,))
    return {"ok": True}

@api_router.get("/marketplace/favorites")
async def get_marketplace_favorites(account: dict = Depends(get_current_account)):
    query = '''
        SELECT i.*, c.name as category_name, 1 as is_saved,
               (SELECT COUNT(*) FROM marketplace_favorites f WHERE f.item_id = i.id) as saves_count
        FROM marketplace_items i
        JOIN marketplace_favorites mf ON i.id = mf.item_id
        LEFT JOIN marketplace_categories c ON i.category_id = c.id
        WHERE mf.user_id = %s
        ORDER BY mf.created_at DESC
    '''
    items = await db_fetchall(query, (account["account_id"],))
    
    if items:
        item_ids = [str(item['id']) for item in items]
        placeholders = ','.join(['%s'] * len(item_ids))
        img_query = f"SELECT item_id, image_url FROM marketplace_images WHERE item_id IN ({placeholders})"
        images = await db_fetchall(img_query, tuple(item_ids))
        
        img_map = {}
        for img in images:
            img_map.setdefault(img['item_id'], []).append(img['image_url'])
            
        for item in items:
            item['images'] = img_map.get(item['id'], [])
            if item.get('created_at'): item['created_at'] = str(item['created_at'])
            if item.get('updated_at'): item['updated_at'] = str(item['updated_at'])
            
    return {"ok": True, "data": items}

@api_router.post("/marketplace/favorites/{item_id}")
async def toggle_marketplace_favorite(item_id: str, account: dict = Depends(get_current_account)):
    existing = await db_fetchone("SELECT id FROM marketplace_favorites WHERE user_id=%s AND item_id=%s", (account["account_id"], item_id))
    if existing:
        await db_execute("DELETE FROM marketplace_favorites WHERE id=%s", (existing["id"],))
        return {"ok": True, "saved": False}
    else:
        await db_execute("INSERT INTO marketplace_favorites (id, user_id, item_id) VALUES (%s, %s, %s)", (str(uuid.uuid4()), account["account_id"], item_id))
        return {"ok": True, "saved": True}

@api_router.post("/marketplace/reports/{item_id}")
async def report_marketplace_item(item_id: str, payload: MarketplaceReportIn, account: dict = Depends(get_current_account)):
    await db_execute("INSERT INTO marketplace_reports (id, item_id, reporter_id, reason) VALUES (%s, %s, %s, %s)", (str(uuid.uuid4()), item_id, account["account_id"], payload.reason))
    return {"ok": True}

@api_router.get("/marketplace/chat/{item_id}")
async def get_marketplace_chat(item_id: str, account: dict = Depends(get_current_account)):
    item = await db_fetchone("SELECT user_id, title FROM marketplace_items WHERE id=%s", (item_id,))
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    query = '''
        SELECT c.*, acc.email, COALESCE(ud.name, emp.name, acc.email) as sender_name,
               (c.sender_id = %s) as is_mine
        FROM marketplace_chat c
        JOIN accounts acc ON c.sender_id = acc.account_id
        LEFT JOIN user_details ud ON acc.user_id = ud.user_id
        LEFT JOIN employees emp ON acc.employee_id = emp.employee_id
        WHERE c.item_id = %s AND (c.sender_id = %s OR c.receiver_id = %s)
        ORDER BY c.created_at ASC
    '''
    messages = await db_fetchall(query, (account["account_id"], item_id, account["account_id"], account["account_id"]))
    
    for msg in messages:
        if msg.get('created_at'): msg['created_at'] = str(msg['created_at'])
        
    return {"ok": True, "data": messages}

@api_router.post("/marketplace/chat/{item_id}")
async def send_marketplace_chat(item_id: str, payload: MarketplaceChatMessageIn, account: dict = Depends(get_current_account)):
    item = await db_fetchone("SELECT user_id FROM marketplace_items WHERE id=%s", (item_id,))
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    # Receiver is the item owner, UNLESS the sender is the item owner, then we need to find who they are replying to?
    # Simple logic: If sender is NOT owner, receiver = owner.
    # If sender IS owner, receiver = whoever they are chatting with... this requires threads!
    # For a simple chat, if sender is owner, we check the latest message they received for this item and reply to them.
    receiver_id = item['user_id']
    if account["account_id"] == item['user_id']:
        last_msg = await db_fetchone("SELECT sender_id FROM marketplace_chat WHERE item_id=%s AND receiver_id=%s ORDER BY created_at DESC LIMIT 1", (item_id, account["account_id"]))
        if last_msg:
            receiver_id = last_msg['sender_id']
        else:
            raise HTTPException(status_code=400, detail="Cannot reply to self without a thread")
            
    await db_execute("INSERT INTO marketplace_chat (id, item_id, sender_id, receiver_id, message) VALUES (%s, %s, %s, %s, %s)", (str(uuid.uuid4()), item_id, account["account_id"], receiver_id, payload.message))
    return {"ok": True}

@api_router.post("/marketplace/views/{item_id}")
async def record_marketplace_view(item_id: str, account: dict = Depends(get_current_account)):
    try:
        await db_execute("INSERT INTO marketplace_views (id, item_id, user_id) VALUES (%s, %s, %s)", (str(uuid.uuid4()), item_id, account["account_id"]))
        await db_execute("UPDATE marketplace_items SET views_count = views_count + 1 WHERE id=%s", (item_id,))
    except Exception:
        pass # Ignore duplicates
    return {"ok": True}

"""

with open("server.py", "r") as f:
    content = f.read()
    
if "# --- Marketplace ---" not in content:
    content = content.replace("app.include_router(api_router)", routes + "\n\napp.include_router(api_router)")
    with open("server.py", "w") as f:
        f.write(content)
    print("Routes appended")
else:
    print("Routes already present")
