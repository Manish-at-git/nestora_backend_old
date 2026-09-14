import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

conn = pymysql.connect(
    host=os.getenv("MYSQL_HOST"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DB"),
    port=int(os.getenv("MYSQL_PORT", 3306)),
    cursorclass=pymysql.cursors.DictCursor,
    ssl={'ssl': True} if os.getenv("MYSQL_HOST") and "aiven" in os.getenv("MYSQL_HOST") else None
)

def fix_null_association_ids():
    try:
        with conn.cursor() as cursor:
            # Find all messages where association_id is 'null'
            cursor.execute("SELECT id, pool_id FROM board_committee_chat WHERE association_id = 'null'")
            messages = cursor.fetchall()
            
            for msg in messages:
                # Find the actual association_id of the committee
                cursor.execute("SELECT association_id FROM committees WHERE id = %s", (msg["pool_id"],))
                committee = cursor.fetchone()
                if committee and committee["association_id"]:
                    cursor.execute(
                        "UPDATE board_committee_chat SET association_id = %s WHERE id = %s",
                        (committee["association_id"], msg["id"])
                    )
            conn.commit()
            print(f"Fixed {len(messages)} messages with 'null' association_id.")
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_null_association_ids()
