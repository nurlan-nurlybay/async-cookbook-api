from sqlmodel import SQLModel, Field
from typing import Optional


from pydantic import EmailStr

# 1. Base Class (Shared Fields)
class SubscriberBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)


# 2. Table Model
class Subscriber(SubscriberBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    is_active: bool = Field(default=True)  # Good practice for "Unsubscribe" logic
