from pydantic import BaseModel
from typing import Optional

class AdminCreateUserIn(BaseModel):
    first_name: str
    last_name: str
    email: str
    contact_number: str
    role_id: str
    association_id: Optional[str] = None

