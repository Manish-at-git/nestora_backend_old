import asyncio
from server import init_pool, db_fetchone, pool, verify_password

async def run():
    await init_pool()
    r = await db_fetchone("SELECT a.email, a.password_hash, r.name FROM accounts a LEFT JOIN roles r ON a.role_id = r.id WHERE a.email='superadmin@nestora.io'")
    
    print("ROLE:", r)
    is_valid = verify_password("Admin@Nestora2026", r['password_hash'])
    print("Password Admin@Nestora2026 is valid:", is_valid)
    
    # Check if there are multiple accounts with this email?
    accounts = await db_fetchone("SELECT COUNT(*) as c FROM accounts WHERE email='superadmin@nestora.io'")
    print("Total accounts with this email:", accounts['c'])
    
    if pool:
        pool.close()
        await pool.wait_closed()

asyncio.run(run())
