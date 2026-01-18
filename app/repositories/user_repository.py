from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User model operations."""
    
    def __init__(self, db: Session):
        super().__init__(User, db)
    
    def get_by_field(self, field_name: str, value: any) -> Optional[User]:
        """Get user by a specific field."""
        return self.db.query(User).filter(getattr(User, field_name) == value).first()
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return self.get_by_field("username", username)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email (case-insensitive lookup)."""
        # Normalize email to lowercase for lookup
        email = email.lower().strip()
        return self.get_by_field("email", email)
    
    def create_user(self, username: str, email: str, password_hash: str, role=None) -> User:
        """Create a new user."""
        from app.models.user import UserRole
        if role is None:
            role = UserRole.MEMBER
        return self.create(
            username=username,
            email=email,
            password_hash=password_hash,
            role=role
        )

