import asyncio
from server import init_pool, db_execute, pool

async def run():
    await init_pool()
    try:
        await db_execute("ALTER TABLE entities MODIFY association_id VARCHAR(150)")
        print("entities updated")
    except Exception as e:
        print("entities error:", e)
        
    try:
        await db_execute("ALTER TABLE features MODIFY icon TEXT")
        print("features updated")
    except Exception as e:
        print("features error:", e)
        
    if pool:
        pool.close()
        await pool.wait_closed()

asyncio.run(run())
