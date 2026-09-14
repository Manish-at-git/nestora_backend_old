import asyncio
import pymysql.cursors
from datetime import datetime, date, timedelta

def iso_format(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, timedelta):
        return str(obj)
    return obj

async def test():
    conn = pymysql.connect(host='127.0.0.1', user='nestora', password='nestora_pass_2026', db='nestora', cursorclass=pymysql.cursors.DictCursor)
    with conn.cursor() as cur:
        account_id = "100defa6-bc15-44ad-88bc-7345b50770aa" # hardik
        is_homeowner = False
        assoc_id = None
        
        # Simulated get_timeline logic
        meeting_where = "WHERE 1=1" 
        
        union_query = f"""
            SELECT 'meeting' AS item_type, m.id, m.created_at 
            FROM meetings m {meeting_where}
            
            UNION ALL
            
            SELECT 'announcement' AS item_type, a.id, a.created_at
            FROM announcements a
            
            UNION ALL
            
            SELECT 'event' AS item_type, e.id, e.created_at
            FROM events e
            
            ORDER BY created_at DESC
            LIMIT 10 OFFSET 0
        """
        cur.execute(union_query)
        timeline_ids = cur.fetchall()
        print("timeline_ids:", timeline_ids)
        
        m_ids = [r['id'] for r in timeline_ids if r['item_type'] == 'meeting']
        
        if m_ids:
            m_format = ','.join(['%s']*len(m_ids))
            m_query = f'''
                SELECT m.*, a.name as association_name, ud.name as organizer_name, ud2.name as created_by_name
                FROM meetings m
                JOIN associations a ON m.association_id = a.id
                LEFT JOIN accounts ac ON m.organizer = ac.account_id
                LEFT JOIN user_details ud ON ac.user_id = ud.user_id
                LEFT JOIN accounts ac2 ON m.created_by = ac2.account_id
                LEFT JOIN user_details ud2 ON ac2.user_id = ud2.user_id
                WHERE m.id IN ({m_format})
            '''
            cur.execute(m_query, tuple(m_ids))
            m_rows = cur.fetchall()
            print("m_rows:", m_rows)
            
            assoc_ids = list(set([r['association_id'] for r in m_rows]))
            if assoc_ids:
                a_fmt = ','.join(['%s'] * len(assoc_ids))
                
                cur.execute(f'''
                    SELECT b.association_id, COUNT(DISTINCT ac.account_id) as count
                    FROM accounts ac
                    JOIN roles r ON ac.role_id = r.id
                    JOIN user_details ud ON ac.user_id = ud.user_id
                    JOIN units u ON ud.unit_id = u.id
                    JOIN blocks b ON u.block_id = b.id
                    WHERE r.name = 'Homeowner' AND b.association_id IN ({a_fmt})
                    GROUP BY b.association_id
                ''', tuple(assoc_ids))
                ho_rows = cur.fetchall()
                print("ho_rows:", ho_rows)
                
                cur.execute(f'''
                    SELECT aa.association_id, COUNT(DISTINCT ac.account_id) as count
                    FROM admin_associations aa
                    JOIN accounts ac ON aa.admin_id = ac.account_id
                    JOIN roles r ON ac.role_id = r.id
                    WHERE r.name = 'Board member' AND aa.association_id IN ({a_fmt})
                    GROUP BY aa.association_id
                ''', tuple(assoc_ids))
                board_rows = cur.fetchall()
                print("board_rows:", board_rows)
                
                cur.execute(f'''
                    SELECT meeting_id, status 
                    FROM meeting_rsvps 
                    WHERE account_id = %s AND meeting_id IN ({a_fmt})
                ''', (account_id,) + tuple(assoc_ids))
                my_att_rows = cur.fetchall()
                print("my_att_rows:", my_att_rows)

asyncio.run(test())
