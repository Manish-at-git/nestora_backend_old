import sys

API_CODE = """
class AssessmentRuleBase(BaseModel):
    frequency: str
    default_amount: float
    due_day_of_month: int

class FineRuleBase(BaseModel):
    fine_type: str
    amount: float
    grace_period_days: int

class AssociationSettingsUpdate(BaseModel):
    end_date: Optional[str] = None
    assessment_rules: Optional[AssessmentRuleBase] = None
    fine_rules: Optional[List[FineRuleBase]] = None

@api_router.get("/admin/associations/{id}/settings")
async def get_association_settings(id: str, account: dict = Depends(require_role(["Super admin", "Admin"]))):
    assoc = await db_fetchone("SELECT onboarding_date, end_date FROM associations WHERE id = %s", (id,))
    if not assoc:
        raise HTTPException(status_code=404, detail="Association not found")
        
    assessment = await db_fetchone("SELECT frequency, default_amount, due_day_of_month FROM assessment_rules WHERE association_id = %s LIMIT 1", (id,))
    fines = await db_fetchall("SELECT id, fine_type, amount, grace_period_days FROM fine_rules WHERE association_id = %s", (id,))
    
    # Format dates
    if assoc.get("onboarding_date"):
        assoc["onboarding_date"] = assoc["onboarding_date"].strftime("%Y-%m-%d") if hasattr(assoc["onboarding_date"], 'strftime') else str(assoc["onboarding_date"])
    if assoc.get("end_date"):
        assoc["end_date"] = assoc["end_date"].strftime("%Y-%m-%d") if hasattr(assoc["end_date"], 'strftime') else str(assoc["end_date"])
        
    return {
        "onboarding_date": assoc.get("onboarding_date"),
        "end_date": assoc.get("end_date"),
        "assessment_rules": assessment,
        "fine_rules": fines
    }

@api_router.put("/admin/associations/{id}/settings")
async def update_association_settings(id: str, payload: AssociationSettingsUpdate, account: dict = Depends(require_role(["Super admin", "Admin"]))):
    import uuid
    # Update end_date in associations
    if payload.end_date is not None:
        await db_execute("UPDATE associations SET end_date = %s WHERE id = %s", (payload.end_date if payload.end_date != "" else None, id))
        
    # Update assessment_rules
    if payload.assessment_rules:
        existing = await db_fetchone("SELECT id FROM assessment_rules WHERE association_id = %s", (id,))
        if existing:
            await db_execute("UPDATE assessment_rules SET frequency=%s, default_amount=%s, due_day_of_month=%s WHERE association_id=%s", 
                             (payload.assessment_rules.frequency, payload.assessment_rules.default_amount, payload.assessment_rules.due_day_of_month, id))
        else:
            await db_execute("INSERT INTO assessment_rules (id, association_id, frequency, default_amount, due_day_of_month) VALUES (%s, %s, %s, %s, %s)",
                             (str(uuid.uuid4()), id, payload.assessment_rules.frequency, payload.assessment_rules.default_amount, payload.assessment_rules.due_day_of_month))
                             
    # Update fine_rules
    if payload.fine_rules is not None:
        # For simplicity, we delete existing and recreate
        await db_execute("DELETE FROM fine_rules WHERE association_id = %s", (id,))
        for fr in payload.fine_rules:
            await db_execute("INSERT INTO fine_rules (id, association_id, fine_type, amount, grace_period_days) VALUES (%s, %s, %s, %s, %s)",
                             (str(uuid.uuid4()), id, fr.fine_type, fr.amount, fr.grace_period_days))
                             
    return {"ok": True, "message": "Settings updated"}

"""

def append_to_server():
    with open("server.py", "r") as f:
        content = f.read()
    
    # insert before the end
    target = 'app.include_router(api_router)'
    if target in content:
        new_content = content.replace(target, API_CODE + "\n" + target)
        with open("server.py", "w") as f:
            f.write(new_content)
        print("Successfully appended API code.")
    else:
        print("Target string not found in server.py")

if __name__ == "__main__":
    append_to_server()
