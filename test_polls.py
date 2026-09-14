import asyncio
from database import db_execute, db_fetchall

async def main():
    polls = await db_fetchall("SELECT * FROM polls ORDER BY created_at DESC LIMIT 1")
    options = await db_fetchall("SELECT * FROM poll_options")
    print("Polls:", polls)
    print("Options:", options)

asyncio.run(main())
