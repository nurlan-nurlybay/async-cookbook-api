from pydantic import BaseModel, EmailStr

class SubscriberCreate(BaseModel):
    email: EmailStr 

class SubscriberRead(BaseModel):
    id: int
    email: EmailStr
