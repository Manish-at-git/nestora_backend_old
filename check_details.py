import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

conn = pymysql.connect(
    host=os.environ['MYSQL_HOST'],
    port=int(os.environ['MYSQL_PORT']),
    user=os.environ['MYSQL_USER'],
    password=os.environ['MYSQL_PASSWORD'],
    database=os.environ['MYSQL_DB'],
    cursorclass=pymysql.cursors.DictCursor
)

with conn.cursor() as cur:
    cur.execute("""
        SELECT ud.user_id, uc.login_code 
        FROM user_details ud 
        JOIN user_codes uc ON uc.id=ud.code_id 
        WHERE uc.login_code LIKE 'NST-DEMO%'
    """)
    rows = cur.fetchall()
    print("User Details found for codes:", [r['login_code'] for r in rows])
