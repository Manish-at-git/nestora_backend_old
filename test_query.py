import sys
sys.path.insert(0, ".")
from server import VendorIn
import uuid

payload_data = {
    "name": "Test Vendor",
    "contact_number": "1234567890",
    "status": "Active"
}
payload = VendorIn(**payload_data)

v_id = str(uuid.uuid4())
cols = []
vals = []

payload_dict = payload.dict()
payload_dict['id'] = v_id

for k, v in payload_dict.items():
    if v is not None:
        cols.append(k)
        vals.append(v)
        
query = f"INSERT INTO vendors ({', '.join(cols)}) VALUES ({', '.join(['%s']*len(cols))})"
print(query)
