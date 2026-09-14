import os

def patch_server():
    path = "server.py"
    with open(path, "r") as f:
        c = f.read()

    new_vendor_code = """class VendorIn(BaseModel):
    name: str
    service_type: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    contact_number: Optional[str] = None
    address: Optional[str] = None
    gst_number: Optional[str] = None
    licence_url: Optional[str] = None
    certificate_url: Optional[str] = None
    status: Optional[str] = "Active"
    
    vendor_code: Optional[str] = None
    vendor_category: Optional[str] = None
    business_name: Optional[str] = None
    mobile_number: Optional[str] = None
    alternate_mobile_number: Optional[str] = None
    website: Optional[str] = None
    whatsapp_number: Optional[str] = None
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    zip_code: Optional[str] = None
    pan_number: Optional[str] = None
    registration_number: Optional[str] = None
    license_number: Optional[str] = None
    trade_license_number: Optional[str] = None
    years_of_experience: Optional[int] = None
    available_days: Optional[str] = None
    working_hours: Optional[str] = None
    emergency_service: Optional[bool] = None
    support_24_7: Optional[bool] = None
    contract_start_date: Optional[str] = None
    contract_end_date: Optional[str] = None
    contract_value: Optional[float] = None
    payment_terms: Optional[str] = None
    contract_document_url: Optional[str] = None
    renewal_reminder: Optional[bool] = None
    bank_account_name: Optional[str] = None
    bank_name: Optional[str] = None
    bank_account_number: Optional[str] = None
    bank_ifsc_code: Optional[str] = None
    bank_upi_id: Optional[str] = None
    gst_certificate_url: Optional[str] = None
    pan_card_url: Optional[str] = None
    business_license_url: Optional[str] = None
    insurance_certificate_url: Optional[str] = None
    agreement_copy_url: Optional[str] = None
    identity_proof_url: Optional[str] = None
    address_proof_url: Optional[str] = None
    other_documents_url: Optional[str] = None
    vendor_rating: Optional[float] = None
    preferred_vendor: Optional[bool] = None
    verified_vendor: Optional[bool] = None
    remarks: Optional[str] = None
    association_name: Optional[str] = None
    assigned_blocks: Optional[str] = None
    assigned_services: Optional[str] = None
    assigned_manager: Optional[str] = None

@api_router.get("/admin/vendors")
async def get_vendors(_: dict = Depends(require_admin)):
    rows = await db_fetchall("SELECT * FROM vendors ORDER BY created_at DESC")
    return {"ok": True, "vendors": rows}

@api_router.post("/admin/vendors")
async def create_vendor(payload: VendorIn, _: dict = Depends(require_admin)):
    import uuid
    v_id = str(uuid.uuid4())
    
    cols = []
    vals = []
    
    # Extract fields from payload that are not None
    payload_dict = payload.dict()
    payload_dict['id'] = v_id
    
    for k, v in payload_dict.items():
        if v is not None:
            cols.append(k)
            vals.append(v)
            
    query = f"INSERT INTO vendors ({', '.join(cols)}) VALUES ({', '.join(['%s']*len(cols))})"
    
    await db_execute(query, tuple(vals))
    return {"ok": True, "message": "Vendor created", "id": v_id}

@api_router.put("/admin/vendors/{id}")
async def update_vendor(id: str, payload: VendorIn, _: dict = Depends(require_admin)):
    cols = []
    vals = []
    
    payload_dict = payload.dict(exclude_unset=True) # Only update fields that are set
    for k, v in payload_dict.items():
        cols.append(f"{k}=%s")
        vals.append(v)
        
    if not cols:
        return {"ok": True, "message": "Nothing to update"}
        
    vals.append(id)
    query = f"UPDATE vendors SET {', '.join(cols)} WHERE id=%s"
    
    await db_execute(query, tuple(vals))
    return {"ok": True, "message": "Vendor updated"}

@api_router.delete("/admin/vendors/{id}")
async def delete_vendor(id: str, _: dict = Depends(require_admin)):
    await db_execute("DELETE FROM vendors WHERE id=%s", (id,))
    return {"ok": True, "message": "Vendor deleted"}"""

    import re
    # We want to replace everything from `class VendorIn(BaseModel):` down to `return {"ok": True, "message": "Vendor deleted"}`
    
    pattern = re.compile(r'class VendorIn\(BaseModel\):.*?return \{"ok": True, "message": "Vendor deleted"\}', re.DOTALL)
    
    if pattern.search(c):
        c = pattern.sub(new_vendor_code, c)
        with open(path, "w") as f:
            f.write(c)
        print("Patched server.py successfully.")
    else:
        print("Could not find the target block in server.py")

if __name__ == "__main__":
    patch_server()
