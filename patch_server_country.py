import os

PATH = "server.py"

def patch():
    with open(PATH, "r") as f:
        content = f.read()

    # 1. Update models
    old_model = """class SubscriptionPlanCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    monthly_price: Optional[float] = None
    yearly_price: Optional[float] = None
    trial_days: Optional[int] = 0
    is_active: Optional[bool] = True

class SubscriptionPlanUpdate(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    monthly_price: Optional[float] = None
    yearly_price: Optional[float] = None
    trial_days: Optional[int] = 0
    is_active: Optional[bool] = True"""
    
    new_model = """class SubscriptionPlanCreate(BaseModel):
    name: str
    code: str
    country: str
    description: Optional[str] = None
    monthly_price: Optional[float] = None
    yearly_price: Optional[float] = None
    trial_days: Optional[int] = 0
    is_active: Optional[bool] = True

class SubscriptionPlanUpdate(BaseModel):
    name: str
    code: str
    country: str
    description: Optional[str] = None
    monthly_price: Optional[float] = None
    yearly_price: Optional[float] = None
    trial_days: Optional[int] = 0
    is_active: Optional[bool] = True"""
    
    content = content.replace(old_model, new_model)

    # 2. Update endpoints
    old_create = """@api_router.post("/admin/subscription-plans")
async def create_subscription_plan(payload: SubscriptionPlanCreate, account: dict = Depends(require_role(["Super admin"]))):
    new_id = await db_execute(
        "INSERT INTO subscription_plans (name, code, description, monthly_price, yearly_price, trial_days, is_active) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (payload.name, payload.code, payload.description, payload.monthly_price, payload.yearly_price, payload.trial_days, payload.is_active)
    )
    return {"ok": True, "id": new_id}"""

    new_create = """@api_router.post("/admin/subscription-plans")
async def create_subscription_plan(payload: SubscriptionPlanCreate, account: dict = Depends(require_role(["Super admin"]))):
    existing = await db_fetchone("SELECT id FROM subscription_plans WHERE name=%s AND country=%s", (payload.name, payload.country))
    if existing:
        raise HTTPException(status_code=400, detail="A plan with this name already exists in this country")
        
    new_id = await db_execute(
        "INSERT INTO subscription_plans (name, code, country, description, monthly_price, yearly_price, trial_days, is_active) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        (payload.name, payload.code, payload.country, payload.description, payload.monthly_price, payload.yearly_price, payload.trial_days, payload.is_active)
    )
    return {"ok": True, "id": new_id}"""
    content = content.replace(old_create, new_create)

    old_update = """@api_router.put("/admin/subscription-plans/{plan_id}")
async def update_subscription_plan(plan_id: str, payload: SubscriptionPlanUpdate, account: dict = Depends(require_role(["Super admin"]))):
    await db_execute(
        "UPDATE subscription_plans SET name=%s, code=%s, description=%s, monthly_price=%s, yearly_price=%s, trial_days=%s, is_active=%s WHERE id=%s",
        (payload.name, payload.code, payload.description, payload.monthly_price, payload.yearly_price, payload.trial_days, payload.is_active, plan_id)
    )
    return {"ok": True}"""

    new_update = """@api_router.put("/admin/subscription-plans/{plan_id}")
async def update_subscription_plan(plan_id: str, payload: SubscriptionPlanUpdate, account: dict = Depends(require_role(["Super admin"]))):
    existing = await db_fetchone("SELECT id FROM subscription_plans WHERE name=%s AND country=%s AND id != %s", (payload.name, payload.country, plan_id))
    if existing:
        raise HTTPException(status_code=400, detail="A plan with this name already exists in this country")
        
    await db_execute(
        "UPDATE subscription_plans SET name=%s, code=%s, country=%s, description=%s, monthly_price=%s, yearly_price=%s, trial_days=%s, is_active=%s WHERE id=%s",
        (payload.name, payload.code, payload.country, payload.description, payload.monthly_price, payload.yearly_price, payload.trial_days, payload.is_active, plan_id)
    )
    return {"ok": True}"""
    content = content.replace(old_update, new_update)

    with open(PATH, "w") as f:
        f.write(content)

    print("Patched server.py successfully")

if __name__ == "__main__":
    patch()
