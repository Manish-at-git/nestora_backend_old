import os

api_code = """
# ---------- Chart of Accounts API ----------
import openpyxl
from io import BytesIO

class AssociationCOACreate(BaseModel):
    account_code: str
    account_name: str
    account_type: str

@api_router.post("/admin/global-coa/upload")
async def upload_global_coa(request: Request, file: UploadFile = File(...), account: dict = Depends(require_role(["Super admin"]))):
    content = await file.read()
    
    # Process Excel file
    try:
        workbook = openpyxl.load_workbook(filename=BytesIO(content), data_only=True)
        sheet = workbook.active
        
        # Assume first row is header, search for code, name, type
        headers = [cell.value.lower() if cell.value else "" for cell in sheet[1]]
        try:
            code_idx = headers.index("account_code")
        except ValueError:
            code_idx = 0
        try:
            name_idx = headers.index("account_name")
        except ValueError:
            name_idx = 1
        try:
            type_idx = headers.index("account_type")
        except ValueError:
            type_idx = 2

        count = 0
        for row in sheet.iter_rows(min_row=2, values_only=True):
            if row[code_idx] and row[name_idx] and row[type_idx]:
                new_id = str(uuid.uuid4())
                await db_execute(
                    "INSERT INTO global_chart_of_accounts (id, account_code, account_name, account_type) VALUES (%s, %s, %s, %s)",
                    (new_id, str(row[code_idx]), str(row[name_idx]), str(row[type_idx]))
                )
                count += 1
        
        return {"ok": True, "message": f"Successfully uploaded {count} global chart of accounts."}
    except Exception as e:
        return JSONResponse(status_code=400, content={"detail": f"Error parsing Excel file: {str(e)}"})

@api_router.get("/admin/global-coa")
async def get_global_coa(request: Request, account: dict = Depends(require_role(["Super admin", "Admin", "Accountant"]))):
    rows = await db_fetchall("SELECT * FROM global_chart_of_accounts ORDER BY account_type, account_code")
    return rows

@api_router.post("/accountant/association-coa/map")
async def map_global_coa(request: Request, association_id: str = Query(..., description="Association ID to map"), account: dict = Depends(require_role(["Accountant", "Super admin", "Admin"]))):
    # Check if this association already mapped
    existing = await db_fetchone("SELECT COUNT(*) as count FROM association_chart_of_accounts WHERE association_id = %s", (association_id,))
    if existing and existing["count"] > 0:
        return JSONResponse(status_code=400, content={"detail": "Chart of Accounts is already mapped for this association."})
        
    global_accounts = await db_fetchall("SELECT * FROM global_chart_of_accounts")
    if not global_accounts:
        return JSONResponse(status_code=400, content={"detail": "Global Chart of Accounts is empty. Please contact Super Admin."})
        
    for g_acc in global_accounts:
        new_id = str(uuid.uuid4())
        await db_execute(
            "INSERT INTO association_chart_of_accounts (id, association_id, account_code, account_name, account_type, mapped_from_global_id) VALUES (%s, %s, %s, %s, %s, %s)",
            (new_id, association_id, g_acc["account_code"], g_acc["account_name"], g_acc["account_type"], g_acc["id"])
        )
        
    return {"ok": True, "message": f"Successfully mapped {len(global_accounts)} accounts."}

@api_router.get("/accountant/association-coa")
async def get_association_coa(request: Request, association_id: str = Query(...), account: dict = Depends(require_role(["Accountant", "Super admin", "Admin"]))):
    rows = await db_fetchall("SELECT * FROM association_chart_of_accounts WHERE association_id = %s ORDER BY account_type, account_code", (association_id,))
    return rows

@api_router.post("/accountant/association-coa")
async def add_association_coa(request: Request, payload: AssociationCOACreate, association_id: str = Query(...), account: dict = Depends(require_role(["Accountant", "Super admin", "Admin"]))):
    new_id = str(uuid.uuid4())
    await db_execute(
        "INSERT INTO association_chart_of_accounts (id, association_id, account_code, account_name, account_type) VALUES (%s, %s, %s, %s, %s)",
        (new_id, association_id, payload.account_code, payload.account_name, payload.account_type)
    )
    return {"ok": True, "id": new_id, "message": "Chart of Account added successfully."}

@api_router.put("/accountant/association-coa/{coa_id}")
async def update_association_coa(request: Request, coa_id: str, payload: AssociationCOACreate, account: dict = Depends(require_role(["Accountant", "Super admin", "Admin"]))):
    await db_execute(
        "UPDATE association_chart_of_accounts SET account_code = %s, account_name = %s, account_type = %s WHERE id = %s",
        (payload.account_code, payload.account_name, payload.account_type, coa_id)
    )
    return {"ok": True, "message": "Chart of Account updated successfully."}

@api_router.delete("/accountant/association-coa/{coa_id}")
async def delete_association_coa(request: Request, coa_id: str, account: dict = Depends(require_role(["Accountant", "Super admin", "Admin"]))):
    await db_execute("DELETE FROM association_chart_of_accounts WHERE id = %s", (coa_id,))
    return {"ok": True, "message": "Chart of Account deleted successfully."}
"""

with open("/Users/hiralgandharva/Desktop/Hardik/OpsisTechnology/Nestora/backend/server.py", "r") as f:
    content = f.read()

if "app.include_router(api_router)" in content:
    content = content.replace("app.include_router(api_router)", api_code + "\\napp.include_router(api_router)")
    with open("/Users/hiralgandharva/Desktop/Hardik/OpsisTechnology/Nestora/backend/server.py", "w") as f:
        f.write(content)
    print("Appended Chart of Accounts API routes.")
else:
    print("Could not find app.include_router to inject routes.")
