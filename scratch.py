import asyncio
from dotenv import load_dotenv
load_dotenv()
from server import init_pool, get_admin_amenity_bookings, db_fetchone

async def main():
    await init_pool()
    account = await db_fetchone("SELECT a.account_id, a.user_id, a.employee_id, a.email, a.role_id, r.name as role FROM accounts a LEFT JOIN roles r ON a.role_id = r.id WHERE a.email = 'hardik91_test2@nestora.ai'")
    print("ACCOUNT:", account)
    
    # Try calling get_admin_amenity_bookings
    try:
        id = "5a16f53c-62e5-4945-b2eb-c73330af5cc6"
        res = await get_admin_amenity_bookings(id, account)
        print("SUCCESS! Returning", len(res), "bookings")
    except Exception as e:
        print("ERROR!", e)

asyncio.run(main())
