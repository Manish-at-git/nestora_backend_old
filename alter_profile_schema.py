import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

conn = mysql.connector.connect(
    host=os.getenv("DB_HOST", "127.0.0.1"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASS", "root"),
    database=os.getenv("DB_NAME", "nestora")
)

cursor = conn.cursor()

# 1. Update user_details
try:
    cursor.execute("ALTER TABLE user_details ADD COLUMN alt_contact_number VARCHAR(30) DEFAULT NULL")
    print("Added alt_contact_number to user_details.")
except Exception as e:
    print("Error or already exists:", e)

try:
    cursor.execute("ALTER TABLE user_details ADD COLUMN profile_pic_url TEXT DEFAULT NULL")
    print("Added profile_pic_url to user_details.")
except Exception as e:
    print("Error or already exists:", e)

# 2. Create family_members
cursor.execute("""
CREATE TABLE IF NOT EXISTS family_members (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  name VARCHAR(150),
  email VARCHAR(150),
  contact_number VARCHAR(30),
  alt_contact_number VARCHAR(30),
  FOREIGN KEY (user_id) REFERENCES user_details(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""")
print("Created family_members table.")

# 3. Create vehicles
cursor.execute("""
CREATE TABLE IF NOT EXISTS vehicles (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  type ENUM('Bike', 'Car'),
  registration_number VARCHAR(50),
  insurance_url TEXT,
  puc_url TEXT,
  FOREIGN KEY (user_id) REFERENCES user_details(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""")
print("Created vehicles table.")

# 4. Create pets
cursor.execute("""
CREATE TABLE IF NOT EXISTS pets (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  type ENUM('Dog', 'Cat'),
  name VARCHAR(50),
  breed VARCHAR(100),
  vaccinated BOOLEAN DEFAULT FALSE,
  vaccination_date DATE,
  next_vaccination_reminder BOOLEAN DEFAULT FALSE,
  FOREIGN KEY (user_id) REFERENCES user_details(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""")
print("Created pets table.")

conn.commit()
cursor.close()
conn.close()
print("Schema updates complete.")
