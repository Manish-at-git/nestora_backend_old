import asyncio
from server import init_pool, db_execute, pool

async def run():
    await init_pool()
    await db_execute("DELETE FROM accounts WHERE email='admin@nestora.io'")
    await db_execute("DELETE FROM accounts WHERE email='superadmin@nestora.io'")
    if pool:
        pool.close()
        await pool.wait_closed()

asyncio.run(run())
