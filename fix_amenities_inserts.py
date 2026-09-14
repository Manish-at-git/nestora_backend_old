import sys

def fix_server():
    with open("server.py", "r") as f:
        content = f.read()

    # Fix create_amenity
    old_create = """@api_router.post("/admin/associations/{id}/amenities")
async def create_amenity(id: str, payload: AmenityCreate, account: dict = Depends(require_role(["Super admin", "Admin"]))):
    import uuid
    new_id = str(uuid.uuid4())
    await db_execute("INSERT INTO amenities (id, association_id, name, charges, status) VALUES (%s, %s, %s, %s, %s)",
                     (new_id, id, payload.name, payload.charges, payload.status))
    return {"ok": True, "id": new_id, "message": "Amenity added successfully"}"""

    new_create = """@api_router.post("/admin/associations/{id}/amenities")
async def create_amenity(id: str, payload: AmenityCreate, account: dict = Depends(require_role(["Super admin", "Admin"]))):
    new_id = await db_execute("INSERT INTO amenities (association_id, name, charges, status) VALUES (%s, %s, %s, %s)",
                     (id, payload.name, payload.charges, payload.status))
    return {"ok": True, "id": new_id, "message": "Amenity added successfully"}"""

    content = content.replace(old_create, new_create)

    # Fix book_amenity
    old_book = """    booking_id = str(uuid.uuid4())
    await db_execute('''
        INSERT INTO amenity_bookings (id, amenity_id, user_id, association_id, unit_number, homeowner_name, amount, booking_date, payment_status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (booking_id, amenity_id, user_id, assoc_id, unit_number, homeowner_name, amenity.get("charges", 0), payload.booking_date, "Confirmed"))"""

    new_book = """    booking_id = await db_execute('''
        INSERT INTO amenity_bookings (amenity_id, user_id, association_id, unit_number, homeowner_name, amount, booking_date, payment_status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ''', (amenity_id, user_id, assoc_id, unit_number, homeowner_name, amenity.get("charges", 0), payload.booking_date, "Confirmed"))"""

    content = content.replace(old_book, new_book)

    with open("server.py", "w") as f:
        f.write(content)
    print("Fixed inserts in server.py")

if __name__ == "__main__":
    fix_server()
