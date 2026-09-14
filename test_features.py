import asyncio
from server import db_fetchall

async def main():
    res = await db_fetchall("SELECT id, name FROM features")
    print("FEATURES:", [r["name"] for r in res])

asyncio.run(main())
