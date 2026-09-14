import sys
sys.path.insert(0, ".")
import asyncio
from server import db_fetchall

async def main():
    try:
        res = await db_fetchall("SHOW CREATE TABLE vendors")
        print(res)
    except Exception as e:
        print(e)
    
    try:
        res = await db_fetchall("SHOW TRIGGERS LIKE 'vendors'")
        print(res)
    except Exception as e:
        print(e)

asyncio.run(main())
