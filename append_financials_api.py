import os

api_code = """
# ---------- Financial Reports API ----------

class FinancialReportCreate(BaseModel):
    association_id: str
    published_month: str
    report_type: str
    title: str
    file_url: str

@api_router.get("/admin/financial-reports")
async def get_financial_reports(request: Request, account: dict = Depends(require_role(["Super admin"]))):
    # Get all reports and also include association name
    query = \"\"\"
        SELECT fr.*, a.name as association_name 
        FROM financial_reports fr
        LEFT JOIN associations a ON fr.association_id = a.id
        ORDER BY fr.created_at DESC
    \"\"\"
    rows = await db_fetchall(query)
    return rows

@api_router.post("/admin/financial-reports")
async def create_financial_report(request: Request, payload: FinancialReportCreate, account: dict = Depends(require_role(["Super admin"]))):
    account = request.state.account
    new_id = str(uuid.uuid4())
    
    await db_execute(
        \"\"\"INSERT INTO financial_reports (
            id, association_id, published_month, report_type, title, file_url, uploaded_by
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)\"\"\",
        (
            new_id, payload.association_id, payload.published_month, 
            payload.report_type, payload.title, payload.file_url, account["account_id"]
        )
    )
    
    return {"ok": True, "id": new_id, "message": "Financial report uploaded successfully."}
"""

with open("/Users/hiralgandharva/Desktop/Hardik/OpsisTechnology/Nestora/backend/server.py", "r") as f:
    content = f.read()

if "app.include_router(api_router)" in content:
    content = content.replace("app.include_router(api_router)", api_code + "\\napp.include_router(api_router)")
    with open("/Users/hiralgandharva/Desktop/Hardik/OpsisTechnology/Nestora/backend/server.py", "w") as f:
        f.write(content)
    print("Appended financial API routes.")
else:
    print("Could not find app.include_router to inject routes.")
