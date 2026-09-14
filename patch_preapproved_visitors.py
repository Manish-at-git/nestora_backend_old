import asyncio
from database import get_db_pool

async def patch_db():
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS pre_approved_visitors (
                    id CHAR(36) PRIMARY KEY,
                    resident_id CHAR(36) NOT NULL,
                    unit_id CHAR(36) NOT NULL,
                    visitor_name VARCHAR(150) NOT NULL,
                    mobile VARCHAR(20) NOT NULL,
                    visitor_type VARCHAR(50) NOT NULL,
                    pass_code VARCHAR(50) UNIQUE NOT NULL,
                    otp VARCHAR(10),
                    visit_date DATE NOT NULL,
                    start_time TIME NOT NULL,
                    end_time TIME NOT NULL,
                    number_of_visitors INT DEFAULT 1,
                    vehicle_number VARCHAR(50),
                    purpose VARCHAR(255),
                    pass_type VARCHAR(50) DEFAULT 'Single Entry',
                    status ENUM('Active', 'Used', 'Expired', 'Cancelled') DEFAULT 'Active',
                    created_by CHAR(36),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (resident_id) REFERENCES user_details(user_id) ON DELETE CASCADE,
                    FOREIGN KEY (unit_id) REFERENCES units(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS visitor_logs (
                    id CHAR(36) PRIMARY KEY,
                    pre_approved_id CHAR(36) NOT NULL,
                    check_in DATETIME DEFAULT CURRENT_TIMESTAMP,
                    check_out DATETIME,
                    gate VARCHAR(50),
                    guard_id CHAR(36),
                    visitor_photo_url VARCHAR(255),
                    remarks TEXT,
                    FOREIGN KEY (pre_approved_id) REFERENCES pre_approved_visitors(id) ON DELETE CASCADE,
                    FOREIGN KEY (guard_id) REFERENCES accounts(id) ON DELETE SET NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            
            await conn.commit()
            print("Database tables created successfully!")

if __name__ == "__main__":
    asyncio.run(patch_db())
