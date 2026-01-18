from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.config import settings
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenData
from app.models.user import User, UserRole

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service for authentication and authorization operations."""
    
    def __init__(self, db: Session):
        """Initialize auth service with database session."""
        self.user_repo = UserRepository(db)
        self.db = db
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> Optional[TokenData]:
        """Decode and validate a JWT token."""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            username: str = payload.get("sub")
            user_id: int = payload.get("user_id")
            role: str = payload.get("role")
            if username is None:
                return None
            return TokenData(
                username=username,
                user_id=user_id,
                role=UserRole(role) if role else None
            )
        except JWTError:
            return None
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user by username and password."""
        user = self.user_repo.get_by_username(username)
        if not user:
            return None
        if not self.verify_password(password, user.password_hash):
            return None
        return user
    
    def register_user(self, username: str, email: str, password: str, role: UserRole = UserRole.MEMBER) -> User:
        """Register a new user."""
        # Normalize email to lowercase (emails are case-insensitive)
        email = email.lower().strip()
        
        # Validate email format (additional check beyond Pydantic)
        if not email or '@' not in email:
            raise ValueError("Invalid email format")
        if len(email) > 255:
            raise ValueError("Email address is too long")
        
        # Check if user already exists
        if self.user_repo.get_by_username(username):
            raise ValueError("Username already registered")
        if self.user_repo.get_by_email(email):
            raise ValueError("Email already registered")
        
        # Hash password and create user
        password_hash = self.get_password_hash(password)
        return self.user_repo.create_user(username, email, password_hash, role)
    
    def can_access_task(self, user: User, task: 'Task') -> bool:
        """Check if user can access a task."""
        from app.models.task import Task, TaskAssignment
        
        # Admin can access all tasks
        if user.role == UserRole.ADMIN:
            return True
        
        # Manager can access all tasks
        if user.role == UserRole.MANAGER:
            return True
        
        # Member can access tasks they created or are assigned to
        if task.created_by == user.id:
            return True
        
        # Check if user is assigned to the task
        assignments = self.db.query(TaskAssignment).filter(
            TaskAssignment.task_id == task.id,
            TaskAssignment.user_id == user.id
        ).first()
        
        return assignments is not None
    
    def can_modify_task(self, user: User, task: 'Task') -> bool:
        """Check if user can modify a task."""
        from app.models.task import Task, TaskAssignment
        
        # Admin and Manager can modify all tasks
        if user.role in [UserRole.ADMIN, UserRole.MANAGER]:
            return True
        
        # Member can modify tasks they created or are assigned to
        if task.created_by == user.id:
            return True
        
        # Check if user is assigned to the task
        assignments = self.db.query(TaskAssignment).filter(
            TaskAssignment.task_id == task.id,
            TaskAssignment.user_id == user.id
        ).first()
        
        return assignments is not None
    
    def can_delete_task(self, user: User, task: 'Task') -> bool:
        """Check if user can delete a task."""
        # Only Admin and Manager can delete tasks
        if user.role in [UserRole.ADMIN, UserRole.MANAGER]:
            return True
        
        # Members can delete tasks they created
        if user.role == UserRole.MEMBER and task.created_by == user.id:
            return True
        
        return False

