import sys
import re

new_routes = """# ---------- Routes: RBAC Admin ----------
@api_router.get("/admin/entity-types")
async def get_entity_types(_: dict = Depends(require_admin)):
    return await db_fetchall("SELECT * FROM entity_types")

@api_router.post("/admin/entity-types")
async def create_entity_type(payload: EntityTypeIn, _: dict = Depends(require_admin)):
    existing = await db_fetchone("SELECT id FROM entity_types WHERE name=%s", (payload.name,))
    if existing: raise HTTPException(400, "Entity Type name already exists.")
    type_id = await db_execute("INSERT INTO entity_types (name, description) VALUES (%s, %s)", (payload.name, payload.description))
    return {"id": type_id, **payload.dict()}

@api_router.put("/admin/entity-types/{item_id}")
async def update_entity_type(item_id: int, payload: EntityTypeIn, _: dict = Depends(require_admin)):
    existing = await db_fetchone("SELECT id FROM entity_types WHERE name=%s AND id!=%s", (payload.name, item_id))
    if existing: raise HTTPException(400, "Entity Type name already exists.")
    await db_execute("UPDATE entity_types SET name=%s, description=%s WHERE id=%s", (payload.name, payload.description, item_id))
    return {"ok": True}

@api_router.delete("/admin/entity-types/{item_id}")
async def delete_entity_type(item_id: int, _: dict = Depends(require_admin)):
    await db_execute("DELETE FROM entity_types WHERE id=%s", (item_id,))
    return {"ok": True}

@api_router.get("/admin/entities")
async def get_entities(_: dict = Depends(require_admin)):
    return await db_fetchall("SELECT * FROM entities")

@api_router.post("/admin/entities")
async def create_entity(payload: EntityIn, _: dict = Depends(require_admin)):
    existing = await db_fetchone("SELECT id FROM entities WHERE name=%s", (payload.name,))
    if existing: raise HTTPException(400, "Entity name already exists.")
    entity_id = await db_execute("INSERT INTO entities (entity_type_id, association_id, name, description) VALUES (%s, %s, %s, %s)", 
                                 (payload.entity_type_id, payload.association_id, payload.name, payload.description))
    return {"id": entity_id, **payload.dict()}

@api_router.put("/admin/entities/{item_id}")
async def update_entity(item_id: int, payload: EntityIn, _: dict = Depends(require_admin)):
    existing = await db_fetchone("SELECT id FROM entities WHERE name=%s AND id!=%s", (payload.name, item_id))
    if existing: raise HTTPException(400, "Entity name already exists.")
    await db_execute("UPDATE entities SET entity_type_id=%s, association_id=%s, name=%s, description=%s WHERE id=%s", 
                     (payload.entity_type_id, payload.association_id, payload.name, payload.description, item_id))
    return {"ok": True}

@api_router.delete("/admin/entities/{item_id}")
async def delete_entity(item_id: int, _: dict = Depends(require_admin)):
    await db_execute("DELETE FROM entities WHERE id=%s", (item_id,))
    return {"ok": True}

@api_router.get("/admin/roles")
async def get_roles(_: dict = Depends(require_admin)):
    return await db_fetchall("SELECT * FROM roles")

@api_router.post("/admin/roles")
async def create_role(payload: RoleIn, _: dict = Depends(require_admin)):
    existing = await db_fetchone("SELECT id FROM roles WHERE name=%s", (payload.name,))
    if existing: raise HTTPException(400, "Role name already exists.")
    role_id = await db_execute("INSERT INTO roles (entity_id, name, description, is_active) VALUES (%s, %s, %s, %s)", 
                               (payload.entity_id, payload.name, payload.description, payload.is_active))
    return {"id": role_id, **payload.dict()}

@api_router.put("/admin/roles/{item_id}")
async def update_role(item_id: int, payload: RoleIn, _: dict = Depends(require_admin)):
    existing = await db_fetchone("SELECT id FROM roles WHERE name=%s AND id!=%s", (payload.name, item_id))
    if existing: raise HTTPException(400, "Role name already exists.")
    await db_execute("UPDATE roles SET entity_id=%s, name=%s, description=%s, is_active=%s WHERE id=%s", 
                     (payload.entity_id, payload.name, payload.description, payload.is_active, item_id))
    return {"ok": True}

@api_router.delete("/admin/roles/{item_id}")
async def delete_role(item_id: int, _: dict = Depends(require_admin)):
    acct = await db_fetchone("SELECT account_id FROM accounts WHERE role_id=%s LIMIT 1", (item_id,))
    if acct: raise HTTPException(400, "Cannot delete Role because it is assigned to an account.")
    await db_execute("DELETE FROM role_feature_permissions WHERE role_id=%s", (item_id,))
    await db_execute("DELETE FROM roles WHERE id=%s", (item_id,))
    return {"ok": True}

@api_router.get("/admin/features")
async def get_admin_features(_: dict = Depends(require_admin)):
    return await db_fetchall("SELECT * FROM features")

@api_router.post("/admin/features")
async def create_feature(payload: FeatureIn, _: dict = Depends(require_admin)):
    existing = await db_fetchone("SELECT id FROM features WHERE name=%s", (payload.name,))
    if existing: raise HTTPException(400, "Feature name already exists.")
    feature_id = await db_execute(
        "INSERT INTO features (name, description, parent_id, icon, url, is_active) VALUES (%s,%s,%s,%s,%s,%s)",
        (payload.name, payload.description, payload.parent_id, payload.icon, payload.url, payload.is_active)
    )
    return {"id": feature_id, **payload.dict()}

@api_router.put("/admin/features/{item_id}")
async def update_feature(item_id: int, payload: FeatureIn, _: dict = Depends(require_admin)):
    existing = await db_fetchone("SELECT id FROM features WHERE name=%s AND id!=%s", (payload.name, item_id))
    if existing: raise HTTPException(400, "Feature name already exists.")
    await db_execute(
        "UPDATE features SET name=%s, description=%s, parent_id=%s, icon=%s, url=%s, is_active=%s WHERE id=%s",
        (payload.name, payload.description, payload.parent_id, payload.icon, payload.url, payload.is_active, item_id)
    )
    if not payload.is_active:
        await db_execute("DELETE FROM role_feature_permissions WHERE feature_id=%s", (item_id,))
    return {"ok": True}

@api_router.delete("/admin/features/{item_id}")
async def delete_feature(item_id: int, _: dict = Depends(require_admin)):
    await db_execute("DELETE FROM role_feature_permissions WHERE feature_id=%s", (item_id,))
    await db_execute("DELETE FROM features WHERE id=%s", (item_id,))
    return {"ok": True}

@api_router.post("/admin/permissions")"""

with open("server.py", "r") as f:
    content = f.read()

# Find the start and end of the block
start_marker = "# ---------- Routes: RBAC Admin ----------"
end_marker = '@api_router.post("/admin/permissions")'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker, start_idx)

if start_idx != -1 and end_idx != -1:
    new_content = content[:start_idx] + new_routes + content[end_idx + len(end_marker):]
    with open("server.py", "w") as f:
        f.write(new_content)
    print("Patched successfully")
else:
    print("Markers not found!")
