import os

def patch_server():
    path = "server.py"
    with open(path, "r") as f:
        c = f.read()

    # We can inject at the end of the admin endpoints, before the Documents API section.
    # We will search for "# Documents API" and inject before it.
    
    vendors_api = """
# ------------------------------------------------------------------------------
# Vendors API
# ------------------------------------------------------------------------------

class VendorIn(BaseModel):
    name: str
    service_type: str
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    contact_number: Optional[str] = None
    address: Optional[str] = None
    gst_number: Optional[str] = None
    licence_url: Optional[str] = None
    certificate_url: Optional[str] = None
    status: Optional[str] = "Active"

@api_router.get("/admin/vendors")
async def get_vendors(_: dict = Depends(require_admin)):
    rows = await db_fetchall("SELECT * FROM vendors ORDER BY created_at DESC")
    return {"ok": True, "vendors": rows}

@api_router.post("/admin/vendors")
async def create_vendor(payload: VendorIn, _: dict = Depends(require_admin)):
    import uuid
    v_id = str(uuid.uuid4())
    await db_execute(
        \"\"\"INSERT INTO vendors (id, name, service_type, contact_person, email, contact_number, address, gst_number, licence_url, certificate_url, status) 
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)\"\"\",
        (v_id, payload.name, payload.service_type, payload.contact_person, payload.email, payload.contact_number, payload.address, payload.gst_number, payload.licence_url, payload.certificate_url, payload.status)
    )
    return {"ok": True, "message": "Vendor created", "id": v_id}

@api_router.put("/admin/vendors/{id}")
async def update_vendor(id: str, payload: VendorIn, _: dict = Depends(require_admin)):
    await db_execute(
        \"\"\"UPDATE vendors SET name=%s, service_type=%s, contact_person=%s, email=%s, contact_number=%s, address=%s, gst_number=%s, licence_url=%s, certificate_url=%s, status=%s WHERE id=%s\"\"\",
        (payload.name, payload.service_type, payload.contact_person, payload.email, payload.contact_number, payload.address, payload.gst_number, payload.licence_url, payload.certificate_url, payload.status, id)
    )
    return {"ok": True, "message": "Vendor updated"}

@api_router.delete("/admin/vendors/{id}")
async def delete_vendor(id: str, _: dict = Depends(require_admin)):
    await db_execute("DELETE FROM vendors WHERE id=%s", (id,))
    return {"ok": True, "message": "Vendor deleted"}

"""

    target_marker = "# ------------------------------------------------------------------------------\n# Documents API"
    if target_marker in c:
        c = c.replace(target_marker, vendors_api + target_marker)
        with open(path, "w") as f:
            f.write(c)
        print("Patched server.py successfully.")
    else:
        print("Could not find the target marker in server.py")

if __name__ == "__main__":
    patch_server()
