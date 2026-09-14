import os

SERVER_PATH = "server.py"

pydantic_models = """
class SubscriptionPlanCreate(BaseModel):
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
    is_active: Optional[bool] = True

class SubscriptionPlanFeatures(BaseModel):
    feature_ids: List[str]

class AssociationSubscriptionUpdate(BaseModel):
    plan_id: Optional[str] = None
    subscription_start: Optional[str] = None
    subscription_end: Optional[str] = None
    payment_status: Optional[str] = None
    renewal_date: Optional[str] = None
    subscription_status: Optional[str] = None

"""

api_endpoints = """
@api_router.get("/admin/subscription-plans")
async def get_subscription_plans(account: dict = Depends(require_role("Super admin"))):
    rows = await db_fetchall("SELECT * FROM subscription_plans ORDER BY created_at DESC")
    plan_features = await db_fetchall("SELECT plan_id, feature_id FROM subscription_plan_features")
    feature_map = {}
    for pf in plan_features:
        feature_map.setdefault(pf['plan_id'], []).append(pf['feature_id'])
    
    for r in rows:
        if r.get('created_at'): r['created_at'] = str(r['created_at'])
        r['monthly_price'] = float(r['monthly_price']) if r['monthly_price'] is not None else None
        r['yearly_price'] = float(r['yearly_price']) if r['yearly_price'] is not None else None
        r['features'] = feature_map.get(r['id'], [])
        
    return {"ok": True, "data": rows}

@api_router.post("/admin/subscription-plans")
async def create_subscription_plan(payload: SubscriptionPlanCreate, account: dict = Depends(require_role("Super admin"))):
    import uuid
    new_id = str(uuid.uuid4())
    await db_execute(
        "INSERT INTO subscription_plans (id, name, code, description, monthly_price, yearly_price, trial_days, is_active) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        (new_id, payload.name, payload.code, payload.description, payload.monthly_price, payload.yearly_price, payload.trial_days, payload.is_active)
    )
    return {"ok": True, "id": new_id}

@api_router.put("/admin/subscription-plans/{plan_id}")
async def update_subscription_plan(plan_id: str, payload: SubscriptionPlanUpdate, account: dict = Depends(require_role("Super admin"))):
    await db_execute(
        "UPDATE subscription_plans SET name=%s, code=%s, description=%s, monthly_price=%s, yearly_price=%s, trial_days=%s, is_active=%s WHERE id=%s",
        (payload.name, payload.code, payload.description, payload.monthly_price, payload.yearly_price, payload.trial_days, payload.is_active, plan_id)
    )
    return {"ok": True}

@api_router.delete("/admin/subscription-plans/{plan_id}")
async def delete_subscription_plan(plan_id: str, account: dict = Depends(require_role("Super admin"))):
    await db_execute("DELETE FROM subscription_plans WHERE id=%s", (plan_id,))
    return {"ok": True}

@api_router.post("/admin/subscription-plans/{plan_id}/features")
async def set_subscription_plan_features(plan_id: str, payload: SubscriptionPlanFeatures, account: dict = Depends(require_role("Super admin"))):
    import uuid
    await db_execute("DELETE FROM subscription_plan_features WHERE plan_id=%s", (plan_id,))
    for fid in payload.feature_ids:
        new_id = str(uuid.uuid4())
        await db_execute(
            "INSERT INTO subscription_plan_features (id, plan_id, feature_id) VALUES (%s, %s, %s)",
            (new_id, plan_id, fid)
        )
    return {"ok": True}

@api_router.put("/admin/associations/{assoc_id}/subscription")
async def update_association_subscription(assoc_id: str, payload: AssociationSubscriptionUpdate, account: dict = Depends(require_role("Super admin"))):
    s_start = payload.subscription_start if payload.subscription_start else None
    s_end = payload.subscription_end if payload.subscription_end else None
    r_date = payload.renewal_date if payload.renewal_date else None
    
    await db_execute(
        "UPDATE associations SET current_plan_id=%s, subscription_start=%s, subscription_end=%s, payment_status=%s, renewal_date=%s, subscription_status=%s WHERE id=%s",
        (payload.plan_id, s_start, s_end, payload.payment_status, r_date, payload.subscription_status, assoc_id)
    )
    return {"ok": True}

"""

def run():
    with open(SERVER_PATH, "r") as f:
        content = f.read()

    # Inject models
    if "class SubscriptionPlanCreate" not in content:
        split_point = "# ---------- Logging ----------"
        parts = content.split(split_point)
        content = parts[0] + pydantic_models + "\n" + split_point + parts[1]

    # Inject endpoints
    if "def get_subscription_plans" not in content:
        split_point2 = "app.include_router(api_router)"
        parts2 = content.split(split_point2)
        content = parts2[0] + api_endpoints + "\n" + split_point2 + parts2[1]

    with open(SERVER_PATH, "w") as f:
        f.write(content)

    print("Patch applied to server.py")

if __name__ == "__main__":
    run()
