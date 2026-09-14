import asyncio
import aiomysql
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

async def main():
    pool = await aiomysql.create_pool(
        host=os.getenv('MYSQL_HOST', '127.0.0.1'),
        port=int(os.getenv('MYSQL_PORT', 3306)),
        user=os.getenv('MYSQL_USER', 'nestora'),
        password=os.getenv('MYSQL_PASSWORD', 'nestora_pass_2026'),
        db=os.getenv('MYSQL_DB', 'nestora')
    )
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # 1. marketplace_categories
            await cur.execute("""
            CREATE TABLE IF NOT EXISTS marketplace_categories (
                id CHAR(36) PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            
            # Seed categories
            categories = ['Furniture', 'Electronics', 'Vehicles', 'Books', 'Home Appliances', 'Sports', 'Baby Products', 'Pet Supplies', 'Fashion', 'Home Decor', 'Garden', 'Others']
            for cat in categories:
                await cur.execute("SELECT id FROM marketplace_categories WHERE name=%s", (cat,))
                if not await cur.fetchone():
                    await cur.execute("INSERT INTO marketplace_categories (id, name) VALUES (%s, %s)", (str(uuid.uuid4()), cat))

            # 2. marketplace_items
            await cur.execute("""
            CREATE TABLE IF NOT EXISTS marketplace_items (
                id CHAR(36) PRIMARY KEY,
                association_id CHAR(36) NOT NULL,
                user_id CHAR(36) NOT NULL,
                category_id CHAR(36) NOT NULL,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                price DECIMAL(10,2),
                condition_state VARCHAR(50),
                brand VARCHAR(100),
                item_age VARCHAR(50),
                location VARCHAR(100),
                contact_number VARCHAR(30),
                is_negotiable BOOLEAN DEFAULT FALSE,
                status ENUM('Active', 'Sold', 'Draft', 'Pending') DEFAULT 'Active',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (association_id) REFERENCES associations(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES accounts(account_id) ON DELETE CASCADE,
                FOREIGN KEY (category_id) REFERENCES marketplace_categories(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            
            # 3. marketplace_images
            await cur.execute("""
            CREATE TABLE IF NOT EXISTS marketplace_images (
                id CHAR(36) PRIMARY KEY,
                item_id CHAR(36) NOT NULL,
                image_url VARCHAR(255) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (item_id) REFERENCES marketplace_items(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            
            # 4. marketplace_favorites
            await cur.execute("""
            CREATE TABLE IF NOT EXISTS marketplace_favorites (
                id CHAR(36) PRIMARY KEY,
                user_id CHAR(36) NOT NULL,
                item_id CHAR(36) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES accounts(account_id) ON DELETE CASCADE,
                FOREIGN KEY (item_id) REFERENCES marketplace_items(id) ON DELETE CASCADE,
                UNIQUE(user_id, item_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            # 5. marketplace_chat
            await cur.execute("""
            CREATE TABLE IF NOT EXISTS marketplace_chat (
                id CHAR(36) PRIMARY KEY,
                item_id CHAR(36) NOT NULL,
                sender_id CHAR(36) NOT NULL,
                receiver_id CHAR(36) NOT NULL,
                message TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (item_id) REFERENCES marketplace_items(id) ON DELETE CASCADE,
                FOREIGN KEY (sender_id) REFERENCES accounts(account_id) ON DELETE CASCADE,
                FOREIGN KEY (receiver_id) REFERENCES accounts(account_id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            # 6. marketplace_reports
            await cur.execute("""
            CREATE TABLE IF NOT EXISTS marketplace_reports (
                id CHAR(36) PRIMARY KEY,
                item_id CHAR(36) NOT NULL,
                reporter_id CHAR(36) NOT NULL,
                reason TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (item_id) REFERENCES marketplace_items(id) ON DELETE CASCADE,
                FOREIGN KEY (reporter_id) REFERENCES accounts(account_id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            # 7. marketplace_views
            await cur.execute("""
            CREATE TABLE IF NOT EXISTS marketplace_views (
                id CHAR(36) PRIMARY KEY,
                item_id CHAR(36) NOT NULL,
                user_id CHAR(36) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (item_id) REFERENCES marketplace_items(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES accounts(account_id) ON DELETE CASCADE,
                UNIQUE(item_id, user_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            # Seed Feature 'Marketplace'
            await cur.execute("SELECT id FROM features WHERE name='Marketplace'")
            f = await cur.fetchone()
            if not f:
                fid = str(uuid.uuid4())
                await cur.execute("INSERT INTO features (id, name, parent_id) VALUES (%s, 'Marketplace', NULL)", (fid,))
            
            await conn.commit()
            print("Marketplace schema created successfully.")
    
    pool.close()
    await pool.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
