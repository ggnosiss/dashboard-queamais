from pydantic import BaseModel, EmailStr
from datetime import datetime


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    name: str
    role: str


class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str = "manager"


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    establishment_ids: list[int] = []

    model_config = {"from_attributes": True}


class UserEstablishmentsUpdate(BaseModel):
    establishment_ids: list[int]
