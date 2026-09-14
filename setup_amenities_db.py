import sqlite3
import os

def init_db():
    try:
        conn = sqlite3.connect('nestora.db')
        cur = conn.cursor()
        
        # Create amenities table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS amenities (
                id TEXT PRIMARY KEY,
                association_id TEXT NOT NULL,
                name TEXT NOT NULL,
                charges REAL DEFAULT 0,
                status BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (association_id) REFERENCES associations (id)
            )
        """)
        
        # Create amenity_bookings table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS amenity_bookings (
                id TEXT PRIMARY KEY,
                amenity_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                association_id TEXT NOT NULL,
                unit_number TEXT,
                homeowner_name TEXT,
                amount REAL DEFAULT 0,
                booking_date DATE NOT NULL,
                payment_status TEXT DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (amenity_id) REFERENCES amenities (id),
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (association_id) REFERENCES associations (id)
            )
        """)
        
        conn.commit()
        print("Amenities tables created successfully.")
    except Exception as e:
        print(f"Error creating amenities tables: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    init_db()
