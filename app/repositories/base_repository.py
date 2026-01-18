from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Type, Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

ModelType = TypeVar("ModelType")


class BaseRepository(ABC, Generic[ModelType]):
    """Base repository class providing common CRUD operations."""
    
    def __init__(self, model: Type[ModelType], db: Session):
        """
        Initialize repository with model and database session.
        
        Args:
            model: SQLAlchemy model class
            db: Database session
        """
        self.model = model
        self.db = db
    
    def create(self, **kwargs) -> ModelType:
        """Create a new record."""
        instance = self.model(**kwargs)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance
    
    def get_by_id(self, id: int) -> Optional[ModelType]:
        """Get a record by ID."""
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get all records with pagination."""
        return self.db.query(self.model).offset(skip).limit(limit).all()
    
    def update(self, id: int, **kwargs) -> Optional[ModelType]:
        """Update a record by ID."""
        instance = self.get_by_id(id)
        if instance:
            for key, value in kwargs.items():
                if value is not None:
                    setattr(instance, key, value)
            self.db.commit()
            self.db.refresh(instance)
        return instance
    
    def delete(self, id: int) -> bool:
        """Delete a record by ID."""
        instance = self.get_by_id(id)
        if instance:
            self.db.delete(instance)
            self.db.commit()
            return True
        return False
    
    def filter_by(self, **kwargs) -> List[ModelType]:
        """Filter records by given criteria."""
        return self.db.query(self.model).filter_by(**kwargs).all()
    
    def count(self, **kwargs) -> int:
        """Count records matching criteria."""
        query = self.db.query(self.model)
        if kwargs:
            query = query.filter_by(**kwargs)
        return query.count()
    
    @abstractmethod
    def get_by_field(self, field_name: str, value: Any) -> Optional[ModelType]:
        """Get a record by a specific field."""
        pass

