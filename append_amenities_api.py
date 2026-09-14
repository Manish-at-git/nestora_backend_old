import sys

API_CODE = """
class AmenityCreate(BaseModel):
    name: str
    charges: float
    status: bool = True

class AmenityUpdateStatus(BaseModel):
    status: bool

class AmenityBookingCreate(BaseModel):
    booking_date: str

@api_router.get("/admin/associations/{id}/amenities")
async def get_admin_amenities(id: str, account: dict = Depends(require_role(["Super admin", "Admin"]))):
    amenities = await db_fetchall("SELECT * FROM amenities WHERE association_id = %s", (id,))
    return amenities

@api_router.post("/admin/associations/{id}/amenities")
async def create_amenity(id: str, payload: AmenityCreate, account: dict = Depends(require_role(["Super admin", "Admin"]))):
    import uuid
    new_id = str(uuid.uuid4())
    await db_execute("INSERT INTO amenities (id, association_id, name, charges, status) VALUES (%s, %s, %s, %s, %s)",
                     (new_id, id, payload.name, payload.charges, payload.status))
    return {"ok": True, "id": new_id, "message": "Amenity added successfully"}

@api_router.put("/admin/associations/{id}/amenities/{amenity_id}")
async def update_amenity_status(id: str, amenity_id: str, payload: AmenityUpdateStatus, account: dict = Depends(require_role(["Super admin", "Admin"]))):
    await db_execute("UPDATE amenities SET status = %s WHERE id = %s AND association_id = %s", (payload.status, amenity_id, id))
    return {"ok": True, "message": "Amenity status updated"}

@api_router.get("/admin/associations/{id}/amenity-bookings")
async def get_admin_amenity_bookings(id: str, account: dict = Depends(require_role(["Super admin", "Admin"]))):
    bookings = await db_fetchall('''
        SELECT b.*, a.name as amenity_name 
        FROM amenity_bookings b 
        JOIN amenities a ON b.amenity_id = a.id
        WHERE b.association_id = %s
        ORDER BY b.booking_date DESC
    ''', (id,))
    return bookings

@api_router.get("/associations/{id}/amenities")
async def get_active_amenities(id: str, account: dict = Depends(get_current_account)):
    # Check if user belongs to association
    if account.get("association_id") != id and account.get("role") != "Super admin":
        raise HTTPException(status_code=403, detail="Not authorized for this association")
    amenities = await db_fetchall("SELECT * FROM amenities WHERE association_id = %s AND status = 1", (id,))
    return amenities

@api_router.post("/amenities/{amenity_id}/book")
async def book_amenity(amenity_id: str, payload: AmenityBookingCreate, account: dict = Depends(get_current_account)):
    import uuid
    amenity = await db_fetchone("SELECT * FROM amenities WHERE id = %s", (amenity_id,))
    if not amenity:
        raise HTTPException(status_code=404, detail="Amenity not found")
    if not amenity.get("status"):
        raise HTTPException(status_code=400, detail="Amenity is currently inactive")
        
    assoc_id = amenity.get("association_id")
    user_id = account.get("id")
    
    # Get user unit details
    user = await db_fetchone("SELECT profile_data FROM users WHERE id = %s", (user_id,))
    import json
    unit_number = ""
    homeowner_name = account.get("name", "")
    if user and user.get("profile_data"):
        try:
            profile = json.loads(user["profile_data"])
            unit_number = profile.get("unit_number", "")
        except:
            pass

    booking_id = str(uuid.uuid4())
    await db_execute('''
        INSERT INTO amenity_bookings (id, amenity_id, user_id, association_id, unit_number, homeowner_name, amount, booking_date, payment_status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (booking_id, amenity_id, user_id, assoc_id, unit_number, homeowner_name, amenity.get("charges", 0), payload.booking_date, "Confirmed"))
    
    return {"ok": True, "booking_id": booking_id, "message": "Amenity booked successfully"}

"""

def append_to_server():
    with open("server.py", "r") as f:
        content = f.read()
    
    # insert before the end
    target = 'app.include_router(api_router)'
    if target in content:
        new_content = content.replace(target, API_CODE + "\\n" + target)
        with open("server.py", "w") as f:
            f.write(new_content)
        print("Successfully appended API code.")
    else:
        print("Target string not found in server.py")

if __name__ == "__main__":
    append_to_server()
