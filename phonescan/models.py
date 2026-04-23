from pydantic import BaseModel

class PhoneRequest(BaseModel):
    phone: str