from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.task import TaskStatus, TaskPriority


class TaskCreate(BaseModel):
    """Schema for creating a task."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[TaskStatus] = TaskStatus.TODO
    priority: Optional[TaskPriority] = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None
    assignee_ids: Optional[List[int]] = []
    tags: Optional[List[str]] = []


class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    assignee_ids: Optional[List[int]] = None
    tags: Optional[List[str]] = None


class BulkTaskUpdate(BaseModel):
    """Schema for bulk updating multiple tasks."""
    task_ids: List[int] = Field(..., min_items=1)
    update_data: TaskUpdate


class TaskResponse(BaseModel):
    """Schema for task response."""
    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    created_by: int
    assignees: List[int] = []
    tags: List[str] = []
    subtask_count: int = 0
    dependency_count: int = 0
    
    class Config:
        from_attributes = True


class SubtaskCreate(BaseModel):
    """Schema for creating a subtask."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[TaskStatus] = TaskStatus.TODO
    priority: Optional[TaskPriority] = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None


class SubtaskUpdate(BaseModel):
    """Schema for updating a subtask."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None


class SubtaskResponse(BaseModel):
    """Schema for subtask response."""
    id: int
    parent_task_id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TaskDependencyCreate(BaseModel):
    """Schema for creating a task dependency."""
    depends_on_task_id: int = Field(..., description="ID of the task this task depends on")


class TaskDependencyResponse(BaseModel):
    """Schema for task dependency response."""
    id: int
    task_id: int
    depends_on_task_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class TaskFilter(BaseModel):
    """Schema for advanced task filtering."""
    status: Optional[List[TaskStatus]] = None
    priority: Optional[List[TaskPriority]] = None
    assignee_ids: Optional[List[int]] = None
    created_by: Optional[int] = None
    tags: Optional[List[str]] = None
    due_date_from: Optional[datetime] = None
    due_date_to: Optional[datetime] = None
    created_from: Optional[datetime] = None
    created_to: Optional[datetime] = None
    has_dependencies: Optional[bool] = None
    has_subtasks: Optional[bool] = None
    logic: Optional[str] = Field("AND", description="Filter logic: 'AND' or 'OR'")

