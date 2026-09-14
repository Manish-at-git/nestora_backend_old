import asyncio
import aiomysql
import os
import uuid
import base64
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
DB_USER = os.getenv("MYSQL_USER", "nestora")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "nestora_pass_2026")
DB_NAME = os.getenv("MYSQL_DB", "nestora")
DB_PORT = int(os.getenv("MYSQL_PORT", 3306))

FEATURES = [
    {"name": "Overview"},
    {"name": "Board Task"},
    {"name": "Service Request"},
    {"name": "Inspection"},
    {"name": "Meetings"},
    {"name": "Committees"},
    {"name": "Election"},
    {"name": "Socials", "children": [
        {"name": "Announcement"},
        {"name": "Events"},
        {"name": "Polls"},
        {"name": "Board Member"},
        {"name": "Committee Member"}
    ]},
    {"name": "Amenities"},
    {"name": "Documents", "children": [
        {"name": "Resident Document"},
        {"name": "Board Document"},
        {"name": "Unit Document"}
    ]},
    {"name": "Financials", "children": [
        {"name": "Balance Sheet"},
        {"name": "Income Statement"},
        {"name": "Delinquency Report"},
        {"name": "Prepaid Report"},
        {"name": "Vendor Aging Report"},
        {"name": "Invoice"},
        {"name": "Bank Transaction"},
        {"name": "Bank Statement"},
        {"name": "Other Report"}
    ]},
    {"name": "Security", "children": [
        {"name": "Visitor Management", "children": [
            {"name": "New Visitor"},
            {"name": "Pre-Approved Visitors"},
            {"name": "Check-In"},
            {"name": "Check-Out"},
            {"name": "Visitor History"}
        ]},
        {"name": "Delivery", "children": [
            {"name": "New Delivery"},
            {"name": "Active Deliveries"},
            {"name": "Delivery History"}
        ]},
        {"name": "Vehicles"},
        {"name": "Staff Entry", "children": [
            {"name": "Search & Verify"},
            {"name": "Active Inside"},
            {"name": "Today's Attendance"},
            {"name": "Blocked Staff"}
        ]},
        {"name": "QR Scanner"},
        {"name": "Incidents"},
        {"name": "Surveillance"}
    ]},
    {"name": "Entity Types", "code": "entity_types"},
    {"name": "Entities", "code": "entities"},
    {"name": "Roles", "code": "roles"},
    {"name": "Features", "code": "features"},
    {"name": "Permissions", "code": "permissions"},
    {"name": "Subscriptions", "code": "subscription_plans"},
    {"name": "Associations", "code": "associations"},
    {"name": "Employees", "code": "employees"},
    {"name": "Users", "code": "users"},
    {"name": "Vendors", "code": "vendors"}
]

def generate_svg_data_url(text):
    label = text[:2].upper()
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
  <rect width="24" height="24" rx="4" fill="#334155"/>
  <text x="12" y="16" font-family="sans-serif" font-size="10" font-weight="bold" fill="#ffffff" text-anchor="middle">{label}</text>
</svg>"""
    encoded = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    return f"data:image/svg+xml;base64,{encoded}"

import re

def slugify(text):
    return re.sub(r'[^a-zA-Z0-9]+', '_', text).strip('_').lower()

ROUTE_MAP = {
    'overview': '/dashboard',
    'board_task': '/board-tasks',
    'service_request': '/service-requests',
    'inspection': '/inspection',
    'meetings': '/meetings',
    'committees': '/committees',
    'election': '/election',
    'socials': '/announcements',
    'announcement': '/announcements',
    'events': '/events',
    'polls': '/polls',
    'board_member': '/board-members',
    'committee_member': '/committee-members',
    'amenities': '/amenities',
    'documents': '/documents',
    'resident_document': '/documents',
    'board_document': '/documents',
    'unit_document': '/unit-documents',
    'financials': '/financials',
    'balance_sheet': '/financials/balance-sheet',
    'income_statement': '/financials/income-statement',
    'delinquency_report': '/financials/delinquency-report',
    'prepaid_report': '/financials/prepaid-report',
    'vendor_aging_report': '/financials/vendor-aging',
    'invoice': '/financials/invoices',
    'bank_transaction': '/financials/bank-transactions',
    'bank_statement': '/financials/bank-statements',
    'other_report': '/financials/other-reports',
    'security': '/security',
    'visitor_management': '/visitor-management',
    'new_visitor': '/visitor-management/new',
    'pre_approved_visitors': '/visitor-management/preapproved',
    'check_in': '/visitor-management/checkin',
    'check_out': '/visitor-management/checkout',
    'visitor_history': '/visitor-management/history',
    'delivery': '/deliveries',
    'new_delivery': '/deliveries/new',
    'active_deliveries': '/deliveries/active',
    'delivery_history': '/deliveries/history',
    'vehicles': '/vehicles',
    'staff_entry': '/staff',
    'search_verify': '/staff/search',
    'active_inside': '/staff/active',
    'today_s_attendance': '/staff/attendance',
    'blocked_staff': '/staff/blocked',
    'qr_scanner': '/qr-scanner',
    'incidents': '/incidents',
    'surveillance': '/surveillance',
    'budget': '/budget',
    'chart_of_account': '/chart-of-accounts',
    'bank': '/bank',
    'marketplace': '/marketplace',
    'wallet': '/wallet',
    'email_activity': '/email-activity',
    'approvals': '/approvals',
    'chat_pool': '/chat',
    'nearby': '/nearby',
    'notification': '/notifications',
    'accounts_payable': '/financials/accounts-payable',
    'accounts_receivable': '/financials/accounts-receivable'
}

async def seed_recursive(cur, feature_list, parent_id=None, start_order=1):
    order_idx = start_order
    for item in feature_list:
        name = item["name"]
        code = item.get("code") or slugify(name)
        url = item.get("url") or ROUTE_MAP.get(code)
        
        await cur.execute("SELECT id FROM features WHERE name=%s", (name,))
            
        row = await cur.fetchone()
        icon_url = generate_svg_data_url(name)
        
        if not row:
            f_id = str(uuid.uuid4())
            await cur.execute(
                "INSERT INTO features (id, name, code, description, parent_id, url, order_index, icon) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (f_id, name, code, f"{name} Feature", parent_id, url, order_idx, icon_url)
            )
            print(f"Added Feature: {name} (code: {code}, url: {url}, order {order_idx})")
        else:
            f_id = row["id"]
            await cur.execute(
                "UPDATE features SET code=COALESCE(code, %s), url=COALESCE(url, %s), description=%s, parent_id=%s, order_index=%s, icon=%s WHERE id=%s",
                (code, url, f"{name} Feature", parent_id, order_idx, icon_url, f_id)
            )
            print(f"Updated Feature: {name} (order {order_idx})")
            
        order_idx += 1
        
        children = item.get("children", [])
        if children:
            order_idx = await seed_recursive(cur, children, parent_id=f_id, start_order=order_idx)
            
    return order_idx

async def run_seed():
    pool = await aiomysql.create_pool(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, db=DB_NAME, port=DB_PORT, autocommit=True
    )
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            # Delete old standalone Visitors if it exists
            await cur.execute("DELETE FROM features WHERE name='Visitors' AND parent_id IS NULL")
            await seed_recursive(cur, FEATURES, parent_id=None, start_order=1)

if __name__ == "__main__":
    asyncio.run(run_seed())
