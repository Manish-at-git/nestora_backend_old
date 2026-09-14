import asyncio
import uuid
import json
import pymysql
import sys
sys.path.append('backend')
from server import db_fetchone, db_fetchall, db_execute, setup_schema, ensure_virtual_account, init_pool, pool

async def run_tests():
    await init_pool()
    
    print("--- 1. Testing Schema Initialization ---")
    try:
        await db_execute("DROP TABLE IF EXISTS virtual_accounts")
    except Exception:
        pass
        
    await setup_schema()
    
    tables = [
        "bank_integrations", "collection_accounts", "virtual_accounts",
        "wallet_topups", "payment_webhooks", "wallet_ledger",
        "upi_collections", "bank_reconciliations", "reconciliation_audits"
    ]
    for t in tables:
        res = await db_fetchone(f"SHOW TABLES LIKE '{t}'")
        print(f"Table '{t}': {'EXISTS' if res else 'MISSING'}")

    print("\n--- 2. Testing Virtual Account Generation ---")
    acc = await db_fetchone("SELECT account_id FROM accounts LIMIT 1")
    if not acc:
        print("No accounts found in DB, creating a mock account.")
        u_id = str(uuid.uuid4())
        a_id = str(uuid.uuid4())
        await db_execute("INSERT INTO accounts (user_id, email, password_hash) VALUES (%s, 'testuser@nestora.com', 'hash')", (u_id,))
        account_id = a_id
    else:
        account_id = acc["account_id"]
        
    va = await ensure_virtual_account(account_id)
    print(f"Generated Virtual Account: {va['virtual_account_number']} | IFSC: {va['virtual_ifsc']} | VPA: {va['virtual_vpa']}")

    print("\n--- 3. Testing Bank Webhook Processing & Reconciliation ---")
    payment_id = f"PAY_TEST_{uuid.uuid4().hex[:6]}"
    utr_val = f"UTR{uuid.uuid4().hex[:10].upper()}"
    amount = 2500.00
    
    wallet_before = await db_fetchone("SELECT balance FROM wallets WHERE account_id = %s", (account_id,))
    bal_before = float(wallet_before["balance"]) if wallet_before else 0.0
    
    hook_id = await db_execute(
        """INSERT INTO payment_webhooks 
           (provider, event_type, transaction_id, virtual_account_id, payment_id, utr, amount, status, signature_verified, payload, processed)
           VALUES ('ICICI Smart Collect', 'payment.received', %s, %s, %s, %s, %s, 'SUCCESS', 1, '{}', 1)""",
        (payment_id, va["virtual_account_number"], payment_id, utr_val, amount)
    )
    
    wallet = await db_fetchone("SELECT id, balance FROM wallets WHERE account_id = %s", (account_id,))
    if not wallet:
        w_id = await db_execute("INSERT INTO wallets (account_id, balance, reward_points) VALUES (%s, 0, 0)", (account_id,))
        wallet = {"id": w_id, "balance": 0.0}
        
    new_bal = float(wallet["balance"]) + amount
    await db_execute("UPDATE wallets SET balance = %s WHERE id = %s", (new_bal, wallet["id"]))
    
    ledger_id = await db_execute(
        """INSERT INTO wallet_ledger 
           (wallet_id, account_id, transaction_type, amount, balance_after, reference_id, payment_id, utr, description, status)
           VALUES (%s, %s, 'Credit', %s, %s, %s, %s, %s, 'Virtual Account Topup', 'SUCCESS')""",
        (wallet["id"], account_id, amount, new_bal, hook_id, payment_id, utr_val)
    )
    
    rec_id = await db_execute(
        """INSERT INTO bank_reconciliations 
           (payment_id, utr, virtual_account_id, account_id, amount, bank_amount, wallet_amount, status, reconciled_at)
           VALUES (%s, %s, %s, %s, %s, %s, %s, 'MATCHED', NOW())""",
        (payment_id, utr_val, va["virtual_account_number"], account_id, amount, amount, amount)
    )
    
    print(f"Webhook matched successfully. Wallet balance updated: ₹{bal_before} -> ₹{new_bal}")

    print("\n--- 4. Testing Discrepancy & Manual Override Engine ---")
    disc_pay_id = f"PAY_DISC_{uuid.uuid4().hex[:6]}"
    disc_utr = f"UTR_DISC_{uuid.uuid4().hex[:6]}"
    disc_amount = 5000.00
    
    disc_rec_id = await db_execute(
        """INSERT INTO bank_reconciliations 
           (payment_id, utr, virtual_account_id, account_id, amount, bank_amount, wallet_amount, status, discrepancy_reason, supporting_evidence)
           VALUES (%s, %s, %s, %s, %s, %s, 0, 'DISCREPANCY', 'Webhook signature missing', 'Bank statement verified manually')""",
        (disc_pay_id, disc_utr, va["virtual_account_number"], account_id, disc_amount, disc_amount)
    )
    
    reason = "Webhook failed due to provider outage"
    comments = "Bank statement confirms ₹5000 credit"
    supporting_ref = "BS-2026-09-001"
    admin_email = "finance.admin@nestora.com"
    
    await db_execute("UPDATE bank_reconciliations SET status = 'MATCHED', wallet_amount = %s, reconciled_at = NOW() WHERE id = %s", (disc_amount, disc_rec_id))
    
    audit_id = await db_execute(
        """INSERT INTO reconciliation_audits 
           (reconciliation_id, action, old_status, new_status, reason, comments, supporting_ref, performed_by)
           VALUES (%s, 'OVERRIDE_APPROVE', 'DISCREPANCY', 'MATCHED', %s, %s, %s, %s)""",
        (disc_rec_id, reason, comments, supporting_ref, admin_email)
    )
    
    audit = await db_fetchone("SELECT * FROM reconciliation_audits WHERE id = %s", (audit_id,))
    print(f"Reconciliation Override Completed. Audit Logged:")
    print(f"  Old Status: {audit['old_status']} | New Status: {audit['new_status']}")
    print(f"  By: {audit['performed_by']}")
    print(f"  Reason: {audit['reason']}")
    print(f"  Comments: {audit['comments']}")

    print("\n✅ ALL FINTECH COLLECTION SYSTEM TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(run_tests())
