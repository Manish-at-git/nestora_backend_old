import re

with open('server.py', 'r') as f:
    lines = f.readlines()

output = []
skip = False
for i, line in enumerate(lines):
    if line.startswith('@api_router.put("/admin/committees/{committee_id}")'):
        output.append(line)
        output.append('async def update_committee(committee_id: str, payload: dict, account: dict = Depends(get_current_account)):\n')
        output.append('    if account["role"] not in ["Super admin", "Admin", "Board member"]:\n')
        output.append('        if not account.get("role_permissions", {}).get("Committees", {}).get("can_update"):\n')
        output.append('            raise HTTPException(403, "Permission denied")\n')
        output.append('    \n')
        output.append('    assoc_id = payload.get("association_id")\n')
        output.append('    if account["role"] == "Board member":\n')
        output.append('        assoc_id = await get_board_member_association(account["account_id"])\n')
        output.append('    \n')
        output.append('    start = payload.get("start_date")\n')
        output.append('    end = payload.get("end_date")\n')
        output.append('    \n')
        output.append('    await db_execute(\n')
        output.append('        "UPDATE committees SET association_id=%s, name=%s, description=%s, start_date=%s, end_date=%s WHERE id=%s",\n')
        output.append('        (assoc_id, payload.get("name"), payload.get("description"), start, end, committee_id)\n')
        output.append('    )\n')
        
        # Now we need to skip the broken lines
        skip = True
        continue
        
    if skip:
        if line.strip().startswith('ho_role = await db_fetchone('):
            skip = False
            output.append(line)
        continue
        
    output.append(line)

with open('server.py', 'w') as f:
    f.writelines(output)
print("Fixed update_committee")
