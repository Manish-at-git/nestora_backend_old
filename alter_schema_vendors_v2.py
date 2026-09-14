import asyncio
import aiomysql
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
DB_USER = os.getenv("MYSQL_USER", "nestora")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "nestora_pass_2026")
DB_NAME = os.getenv("MYSQL_DB", "nestora")
DB_PORT = int(os.getenv("MYSQL_PORT", 3306))

async def main():
    pool = await aiomysql.create_pool(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, db=DB_NAME, port=DB_PORT, autocommit=True
    )
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            print("Altering vendors table...")
            
            # List of (column_name, definition)
            columns = [
                ("vendor_code", "VARCHAR(100)"),
                ("vendor_category", "VARCHAR(150)"),
                ("business_name", "VARCHAR(255)"),
                ("mobile_number", "VARCHAR(50)"),
                ("alternate_mobile_number", "VARCHAR(50)"),
                ("website", "VARCHAR(255)"),
                ("whatsapp_number", "VARCHAR(50)"),
                ("address_line_1", "TEXT"),
                ("address_line_2", "TEXT"),
                ("city", "VARCHAR(100)"),
                ("state", "VARCHAR(100)"),
                ("country", "VARCHAR(100)"),
                ("zip_code", "VARCHAR(50)"),
                ("pan_number", "VARCHAR(50)"),
                ("registration_number", "VARCHAR(100)"),
                ("license_number", "VARCHAR(100)"),
                ("trade_license_number", "VARCHAR(100)"),
                ("years_of_experience", "INT"),
                ("available_days", "TEXT"),
                ("working_hours", "VARCHAR(100)"),
                ("emergency_service", "BOOLEAN"),
                ("support_24_7", "BOOLEAN"),
                ("contract_start_date", "DATE"),
                ("contract_end_date", "DATE"),
                ("contract_value", "DECIMAL(15,2)"),
                ("payment_terms", "VARCHAR(255)"),
                ("contract_document_url", "TEXT"),
                ("renewal_reminder", "BOOLEAN"),
                ("bank_account_name", "VARCHAR(150)"),
                ("bank_name", "VARCHAR(150)"),
                ("bank_account_number", "VARCHAR(100)"),
                ("bank_ifsc_code", "VARCHAR(50)"),
                ("bank_upi_id", "VARCHAR(100)"),
                ("gst_certificate_url", "TEXT"),
                ("pan_card_url", "TEXT"),
                ("business_license_url", "TEXT"),
                ("insurance_certificate_url", "TEXT"),
                ("agreement_copy_url", "TEXT"),
                ("identity_proof_url", "TEXT"),
                ("address_proof_url", "TEXT"),
                ("other_documents_url", "TEXT"),
                ("vendor_rating", "DECIMAL(3,1)"),
                ("preferred_vendor", "BOOLEAN"),
                ("verified_vendor", "BOOLEAN"),
                ("remarks", "TEXT"),
                ("association_name", "VARCHAR(255)"),
                ("assigned_blocks", "TEXT"),
                ("assigned_services", "TEXT"),
                ("assigned_manager", "VARCHAR(150)")
            ]
            
            for col_name, col_def in columns:
                try:
                    await cur.execute(f"ALTER TABLE vendors ADD COLUMN {col_name} {col_def}")
                    print(f"Added column {col_name}")
                except aiomysql.Error as e:
                    # Duplicate column error is 1060
                    if e.args[0] == 1060:
                        print(f"Column {col_name} already exists.")
                    else:
                        print(f"Error adding {col_name}: {e}")
                        
            print("Done.")

if __name__ == "__main__":
    asyncio.run(main())
