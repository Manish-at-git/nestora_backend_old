import os

PATH = "server.py"

def patch():
    with open(PATH, "r") as f:
        content = f.read()

    # Fix create_subscription_plan
    original_create = """
@api_router.post("/admin/subscription-plans")
async def create_subscription_plan(payload: SubscriptionPlanCreate, account: dict = Depends(require_role(["Super admin"]))):
    import uuid
    new_id = str(uuid.uuid4())
    await db_execute(
        "INSERT INTO subscription_plans (id, name, code, description, monthly_price, yearly_price, trial_days, is_active) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        (new_id, payload.name, payload.code, payload.description, payload.monthly_price, payload.yearly_price, payload.trial_days, payload.is_active)
    )
    return {"ok": True, "id": new_id}
"""
    new_create = """
@api_router.post("/admin/subscription-plans")
async def create_subscription_plan(payload: SubscriptionPlanCreate, account: dict = Depends(require_role(["Super admin"]))):
    new_id = await db_execute(
        "INSERT INTO subscription_plans (name, code, description, monthly_price, yearly_price, trial_days, is_active) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (payload.name, payload.code, payload.description, payload.monthly_price, payload.yearly_price, payload.trial_days, payload.is_active)
    )
    return {"ok": True, "id": new_id}
"""
    content = content.replace(original_create.strip(), new_create.strip())

    # Fix set_subscription_plan_features
    original_set_features = """
@api_router.post("/admin/subscription-plans/{plan_id}/features")
async def set_subscription_plan_features(plan_id: str, payload: SubscriptionPlanFeatures, account: dict = Depends(require_role(["Super admin"]))):
    import uuid
    await db_execute("DELETE FROM subscription_plan_features WHERE plan_id=%s", (plan_id,))
    for fid in payload.feature_ids:
        new_id = str(uuid.uuid4())
        await db_execute(
            "INSERT INTO subscription_plan_features (id, plan_id, feature_id) VALUES (%s, %s, %s)",
            (new_id, plan_id, fid)
        )
    return {"ok": True}
"""
    new_set_features = """
@api_router.post("/admin/subscription-plans/{plan_id}/features")
async def set_subscription_plan_features(plan_id: str, payload: SubscriptionPlanFeatures, account: dict = Depends(require_role(["Super admin"]))):
    await db_execute("DELETE FROM subscription_plan_features WHERE plan_id=%s", (plan_id,))
    for fid in payload.feature_ids:
        await db_execute(
            "INSERT INTO subscription_plan_features (plan_id, feature_id) VALUES (%s, %s)",
            (plan_id, fid)
        )
    return {"ok": True}
"""
    content = content.replace(original_set_features.strip(), new_set_features.strip())

    with open(PATH, "w") as f:
        f.write(content)

    print("Patched server.py successfully")

if __name__ == "__main__":
    patch()
