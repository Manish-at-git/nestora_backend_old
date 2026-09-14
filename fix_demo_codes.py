import pymysql
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

conn = pymysql.connect(
    host=os.environ['MYSQL_HOST'],
    port=int(os.environ['MYSQL_PORT']),
    user=os.environ['MYSQL_USER'],
    password=os.environ['MYSQL_PASSWORD'],
    database=os.environ['MYSQL_DB'],
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True
)

with conn.cursor() as cur:
    cur.execute("SELECT id, login_code FROM user_codes WHERE login_code LIKE 'NST-DEMO%' AND status='active'")
    codes = cur.fetchall()
    
    for code in codes:
        code_id = code['id']
        login_code = code['login_code']
        # Check if user_details already exists
        cur.execute("SELECT user_id FROM user_details WHERE code_id=%s", (code_id,))
        if cur.fetchone():
            print(f"Details already exist for {login_code}")
            continue
            
        user_id = str(uuid.uuid4())
        name = f"Test User {login_code}"
        email = f"test_{login_code.lower()}@nestora.io"
        
        cur.execute("""
            INSERT INTO user_details (user_id, code_id, name, email, contact_number, address)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, code_id, name, email, '1234567890', 'Test Address'))
        print(f"Inserted details for {login_code}")
