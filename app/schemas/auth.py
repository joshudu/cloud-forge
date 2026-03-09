from pydantic import BaseModel, EmailStr
from uuid import UUID

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    tenant_name: str

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenRefresh(BaseModel):
    refresh_token: str