import sys
sys.path.insert(0, ".")
from server import VendorIn
import uuid

payload = VendorIn(name="Test")
payload_dict = payload.dict()
payload_dict['id'] = str(uuid.uuid4())

cols = []
vals = []
for k, v in payload_dict.items():
    if v is not None:
        cols.append(k)
        vals.append(v)
print("cols:", cols)
print("id count in cols:", cols.count("id"))
