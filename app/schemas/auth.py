from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from app.models.user import UserRole


class UserCreate(BaseModel):
    """Schema for user registration."""
    username: str
    email: EmailStr
    password: str
    role: Optional[UserRole] = UserRole.MEMBER
    
    @field_validator('email', mode='before')
    @classmethod
    def normalize_email(cls, v: str) -> str:
        """Normalize email address to lowercase and strip whitespace."""
        if isinstance(v, str):
            # Normalize email to lowercase (emails are case-insensitive)
            email = v.lower().strip()
            # Check length (EmailStr will handle format validation)
            if len(email) > 255:
                raise ValueError('Email address is too long (max 255 characters)')
            return email
        return v


class UserResponse(BaseModel):
    """Schema for user response."""
    id: int
    username: str
    email: str
    role: UserRole
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    """Schema for login request (JSON)."""
    username: str
    password: str


class TokenData(BaseModel):
    """Schema for token data."""
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[UserRole] = None

