import os

api_code = """
# ---------- Bank Accounts API ----------

class BankAccountCreateUpdate(BaseModel):
    association_id: str
    account_name: str
    account_holder_name: str
    bank_name: str
    account_number: str
    ifsc_code: str
    branch_name: Optional[str] = None
    account_type: str
    currency: str = "INR"
    upi_id: Optional[str] = None
    qr_code_url: Optional[str] = None
    gateway_provider: Optional[str] = None
    merchant_id: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    webhook_secret: Optional[str] = None
    is_default: Optional[bool] = False
    status: Optional[str] = "Active"

@api_router.get("/admin/bank-accounts")
@require_role(["Super admin"])
async def get_bank_accounts(request: Request, association_id: Optional[str] = None):
    query = "SELECT * FROM association_bank_accounts"
    params = ()
    if association_id:
        query += " WHERE association_id = %s"
        params = (association_id,)
    query += " ORDER BY created_at DESC"
    
    rows = await db_fetchall(query, params)
    
    # Mask sensitive data before returning to frontend
    for r in rows:
        dec_acc = decrypt_data(r.get("account_number"))
        if dec_acc and len(dec_acc) > 4:
            r["account_number"] = f"********{dec_acc[-4:]}"
        else:
            r["account_number"] = "****"
            
        r["api_key"] = "****" if r.get("api_key") else None
        r["api_secret"] = "****" if r.get("api_secret") else None
        r["webhook_secret"] = "****" if r.get("webhook_secret") else None
        
    return rows

@api_router.post("/admin/bank-accounts")
@require_role(["Super admin"])
async def create_bank_account(request: Request, payload: BankAccountCreateUpdate):
    account = request.state.account
    new_id = str(uuid.uuid4())
    
    enc_acc = encrypt_data(payload.account_number)
    enc_api = encrypt_data(payload.api_key)
    enc_sec = encrypt_data(payload.api_secret)
    enc_wh = encrypt_data(payload.webhook_secret)
    
    await db_execute(
        \"\"\"INSERT INTO association_bank_accounts (
            id, association_id, account_name, account_holder_name, bank_name,
            account_number, ifsc_code, branch_name, account_type, currency,
            upi_id, qr_code_url, gateway_provider, merchant_id,
            api_key, api_secret, webhook_secret, is_default, status, created_by
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)\"\"\",
        (
            new_id, payload.association_id, payload.account_name, payload.account_holder_name,
            payload.bank_name, enc_acc, payload.ifsc_code, payload.branch_name, payload.account_type,
            payload.currency, payload.upi_id, payload.qr_code_url, payload.gateway_provider,
            payload.merchant_id, enc_api, enc_sec, enc_wh, payload.is_default, payload.status, account["account_id"]
        )
    )
    
    # Audit log
    await log_audit(
        entity_name="association_bank_accounts",
        entity_id=new_id,
        action="CREATE",
        changes={"account_name": payload.account_name, "bank_name": payload.bank_name},
        performed_by=account["account_id"]
    )
    
    return {"ok": True, "id": new_id, "message": "Bank account created securely."}

@api_router.put("/admin/bank-accounts/{account_id}")
@require_role(["Super admin"])
async def update_bank_account(request: Request, account_id: str, payload: BankAccountCreateUpdate):
    acc = request.state.account
    existing = await db_fetchone("SELECT * FROM association_bank_accounts WHERE id = %s", (account_id,))
    if not existing:
        raise HTTPException(status_code=404, detail="Bank account not found")
        
    # Only update sensitive fields if they are actually provided and not masked
    enc_acc = existing["account_number"]
    if payload.account_number and payload.account_number != "****" and not payload.account_number.startswith("****"):
        enc_acc = encrypt_data(payload.account_number)
        
    enc_api = existing["api_key"]
    if payload.api_key and payload.api_key != "****":
        enc_api = encrypt_data(payload.api_key)
        
    enc_sec = existing["api_secret"]
    if payload.api_secret and payload.api_secret != "****":
        enc_sec = encrypt_data(payload.api_secret)
        
    enc_wh = existing["webhook_secret"]
    if payload.webhook_secret and payload.webhook_secret != "****":
        enc_wh = encrypt_data(payload.webhook_secret)

    await db_execute(
        \"\"\"UPDATE association_bank_accounts SET
            association_id=%s, account_name=%s, account_holder_name=%s, bank_name=%s,
            account_number=%s, ifsc_code=%s, branch_name=%s, account_type=%s, currency=%s,
            upi_id=%s, qr_code_url=%s, gateway_provider=%s, merchant_id=%s,
            api_key=%s, api_secret=%s, webhook_secret=%s, is_default=%s, status=%s, updated_by=%s
        WHERE id=%s\"\"\",
        (
            payload.association_id, payload.account_name, payload.account_holder_name,
            payload.bank_name, enc_acc, payload.ifsc_code, payload.branch_name, payload.account_type,
            payload.currency, payload.upi_id, payload.qr_code_url, payload.gateway_provider,
            payload.merchant_id, enc_api, enc_sec, enc_wh, payload.is_default, payload.status,
            acc["account_id"], account_id
        )
    )
    
    await log_audit(
        entity_name="association_bank_accounts",
        entity_id=account_id,
        action="UPDATE",
        changes={"account_name": payload.account_name, "status": payload.status},
        performed_by=acc["account_id"]
    )
    
    return {"ok": True, "message": "Bank account updated securely."}

@api_router.delete("/admin/bank-accounts/{account_id}")
@require_role(["Super admin"])
async def delete_bank_account(request: Request, account_id: str):
    acc = request.state.account
    existing = await db_fetchone("SELECT * FROM association_bank_accounts WHERE id = %s", (account_id,))
    if not existing:
        raise HTTPException(status_code=404, detail="Bank account not found")
        
    await db_execute("DELETE FROM association_bank_accounts WHERE id = %s", (account_id,))
    
    await log_audit(
        entity_name="association_bank_accounts",
        entity_id=account_id,
        action="DELETE",
        changes={"account_name": existing["account_name"]},
        performed_by=acc["account_id"]
    )
    
    return {"ok": True, "message": "Bank account deleted successfully."}

"""

with open("/Users/hiralgandharva/Desktop/Hardik/OpsisTechnology/Nestora/backend/server.py", "r") as f:
    content = f.read()
    
# Insert before app.include_router(api_router)
if "app.include_router(api_router)" in content:
    content = content.replace("app.include_router(api_router)", api_code + "\\napp.include_router(api_router)")
    with open("/Users/hiralgandharva/Desktop/Hardik/OpsisTechnology/Nestora/backend/server.py", "w") as f:
        f.write(content)
    print("Appended bank API routes.")
else:
    print("Could not find app.include_router to inject routes.")
