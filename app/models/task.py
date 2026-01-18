from sqlalchemy import Column, Integer, String, Text, Enum, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime
from app.database import Base


class TaskStatus(str, enum.Enum):
    """Task status enumeration."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"


class TaskPriority(str, enum.Enum):
    """Task priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"




class Task(Base):
    """Task model representing a task in the system."""
    
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO, nullable=False, index=True)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False, index=True)
    due_date = Column(DateTime, nullable=True, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Relationships
    creator = relationship("User", back_populates="created_tasks", foreign_keys=[created_by])
    assignments = relationship("TaskAssignment", back_populates="task", cascade="all, delete-orphan")
    subtasks = relationship("Subtask", back_populates="parent_task", cascade="all, delete-orphan")
    dependencies = relationship(
        "TaskDependency",
        foreign_keys="TaskDependency.task_id",
        back_populates="task",
        cascade="all, delete-orphan"
    )
    blocking_tasks = relationship(
        "TaskDependency",
        foreign_keys="TaskDependency.depends_on_task_id",
        back_populates="depends_on_task",
        cascade="all, delete-orphan"
    )
    tags = relationship("TaskTag", back_populates="task", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Task(id={self.id}, title={self.title}, status={self.status})>"


class Subtask(Base):
    """Subtask model for nested tasks."""
    
    __tablename__ = "subtasks"
    
    id = Column(Integer, primary_key=True, index=True)
    parent_task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO, nullable=False)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False)
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    parent_task = relationship("Task", back_populates="subtasks")
    
    def __repr__(self):
        return f"<Subtask(id={self.id}, title={self.title}, parent_task_id={self.parent_task_id})>"


class TaskDependency(Base):
    """Task dependency model for blocking relationships."""
    
    __tablename__ = "task_dependencies"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    depends_on_task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Relationships
    task = relationship("Task", foreign_keys=[task_id], back_populates="dependencies")
    depends_on_task = relationship("Task", foreign_keys=[depends_on_task_id], back_populates="blocking_tasks")
    
    def __repr__(self):
        return f"<TaskDependency(task_id={self.task_id}, depends_on_task_id={self.depends_on_task_id})>"


class TaskAssignment(Base):
    """Task assignment model for tracking task assignments."""
    
    __tablename__ = "task_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    assigned_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Relationships
    task = relationship("Task")
    user = relationship("User", back_populates="assigned_tasks")
    
    def __repr__(self):
        return f"<TaskAssignment(task_id={self.task_id}, user_id={self.user_id})>"


class TaskTag(Base):
    """Task tag model for categorizing tasks."""
    
    __tablename__ = "task_tags"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    tag = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Relationships
    task = relationship("Task", back_populates="tags")
    
    def __repr__(self):
        return f"<TaskTag(id={self.id}, task_id={self.task_id}, tag={self.tag})>"

