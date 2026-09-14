import os

PATH = "server.py"

def patch():
    with open(PATH, "r") as f:
        content = f.read()

    # 1. Update endpoint signature
    old_sig = """async def onboard_association(
    entity_id: str = Form(...),
    contract_file: UploadFile = File(None),
    csv_file: UploadFile = File(...),
    account: dict = Depends(require_admin)
):"""
    new_sig = """async def onboard_association(
    entity_id: str = Form(...),
    plan_id: str = Form(None),
    contract_file: UploadFile = File(None),
    csv_file: UploadFile = File(...),
    account: dict = Depends(require_admin)
):"""
    content = content.replace(old_sig, new_sig)

    # 2. Update insert query
    old_insert = """    assoc_id = await db_execute(
        \"\"\"INSERT INTO associations (name, association_code, entity_id, address_line_1, address_line_2, city, state, pincode, country, url, contract_url) 
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)\"\"\",
        (assoc_name, assoc_code, entity_id, addr1, addr2, city, state, pincode, country, assoc_url, contract_url)
    )"""
    new_insert = """    from datetime import datetime
    assoc_id = await db_execute(
        \"\"\"INSERT INTO associations (name, association_code, entity_id, address_line_1, address_line_2, city, state, pincode, country, url, contract_url, current_plan_id, subscription_status, subscription_start) 
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)\"\"\",
        (assoc_name, assoc_code, entity_id, addr1, addr2, city, state, pincode, country, assoc_url, contract_url, plan_id, 'Active' if plan_id else 'Trial', datetime.utcnow() if plan_id else None)
    )"""
    content = content.replace(old_insert, new_insert)

    with open(PATH, "w") as f:
        f.write(content)
        
    print("Patched server.py successfully!")

if __name__ == "__main__":
    patch()
