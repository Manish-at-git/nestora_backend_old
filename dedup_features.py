import asyncio
import aiomysql
import os
from dotenv import load_dotenv

load_dotenv()

async def deduplicate():
    pool = await aiomysql.create_pool(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        user=os.getenv("MYSQL_USER", "nestora"),
        password=os.getenv("MYSQL_PASSWORD", "nestora_pass_2026"),
        db=os.getenv("MYSQL_DB", "nestora"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        autocommit=True
    )
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT name, COUNT(*) as c FROM features GROUP BY name HAVING c > 1")
            dups = await cur.fetchall()
            
            for dup in dups:
                name = dup["name"]
                await cur.execute("SELECT id, parent_id FROM features WHERE name=%s ORDER BY parent_id IS NOT NULL DESC, id ASC", (name,))
                rows = await cur.fetchall()
                # Keep the first one
                keep_id = rows[0]["id"]
                # Delete the rest
                for row in rows[1:]:
                    await cur.execute("DELETE FROM features WHERE id=%s", (row["id"],))
                    print(f"Deleted duplicate {name} with id {row['id']}")

if __name__ == "__main__":
    asyncio.run(deduplicate())
