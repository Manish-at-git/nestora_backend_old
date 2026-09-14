import asyncio
from server import init_pool, db_execute, pool

async def run():
    await init_pool()
    try:
        # Check if columns exist, if not add them. We can just run ALTER IGNORE or catch errors.
        try:
            await db_execute("ALTER TABLE entities ADD COLUMN association_id INT NULL")
            print("Added association_id to entities")
        except Exception as e:
            print("Could not add association_id to entities:", e)

        try:
            await db_execute("ALTER TABLE roles ADD COLUMN is_active BOOLEAN DEFAULT TRUE")
            print("Added is_active to roles")
        except Exception as e:
            print("Could not add is_active to roles:", e)

        try:
            await db_execute("ALTER TABLE features ADD COLUMN is_active BOOLEAN DEFAULT TRUE")
            print("Added is_active to features")
        except Exception as e:
            print("Could not add is_active to features:", e)
    finally:
        if pool:
            pool.close()
            await pool.wait_closed()

asyncio.run(run())
