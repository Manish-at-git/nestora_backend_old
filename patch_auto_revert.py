import re

with open("server.py", "r") as f:
    content = f.read()

new_code = """
async def check_expired_board_members():
    while True:
        try:
            # fetch expired board members with active status
            expired = await db_fetchall('''
                SELECT bm.id, bm.account_id 
                FROM board_members bm
                WHERE bm.status = 'active' AND bm.term_end_date < CURRENT_DATE()
            ''')
            if expired:
                role = await db_fetchone("SELECT id FROM roles WHERE name='Homeowner'")
                homeowner_role_id = role["id"]
                for b in expired:
                    # Update status to past
                    await db_execute("UPDATE board_members SET status = 'past' WHERE id = %s", (b["id"],))
                    # Update account role to homeowner
                    await db_execute("UPDATE accounts SET role_id = %s WHERE account_id = %s", (homeowner_role_id, b["account_id"]))
                    logger.info(f"Auto-reverted board member {b['account_id']} to Homeowner")
        except Exception as e:
            logger.error(f"Error checking expired board members: {e}")
            
        await asyncio.sleep(3600)  # Check every hour

@app.on_event("startup")
async def on_startup():
    await init_pool()
    await setup_schema()
    await seed_database()
    await seed_demo_codes()
    await seed_demo_content()
    asyncio.create_task(check_expired_board_members())
    logger.info("Nestora API started (MySQL connected).")
"""

old_code = """
@app.on_event("startup")
async def on_startup():
    await init_pool()
    await setup_schema()
    await seed_database()
    await seed_demo_codes()
    await seed_demo_content()
    logger.info("Nestora API started (MySQL connected).")
"""

if "check_expired_board_members" not in content:
    content = content.replace(old_code.strip(), new_code.strip())
    with open("server.py", "w") as f:
        f.write(content)
