from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from typing import Optional
class UserBase(BaseModel):
    username: str
    email: EmailStr
    
    @validator('username')
    def validate_username(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Username cannot be empty')
        if len(v) > 50:
            raise ValueError('Username cannot be longer than 50 characters')
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, underscores and hyphens')
        return v
class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        if not any(c.isalpha() for c in v):
            raise ValueError('Password must contain at least one letter')
        return v
class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
class RefreshTokenRequest(BaseModel):
    refresh_token: str
class TokenData(BaseModel):
    username: Optional[str] = None
