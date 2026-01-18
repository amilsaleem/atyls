from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.dependencies import get_current_active_user, require_role
from app.models.user import User, UserRole
from app.services.auth_service import AuthService
from app.services.task_service import TaskService
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    SubtaskCreate,
    SubtaskUpdate,
    SubtaskResponse,
    TaskDependencyCreate,
    TaskDependencyResponse,
    BulkTaskUpdate,
    TaskFilter,
)
from app.models.task import TaskStatus, TaskPriority

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new task."""
    task_service = TaskService(db)
    task = task_service.create_task(task_data, current_user.id)
    return task_service.task_to_response(task)


@router.get("", response_model=List[TaskResponse])
def get_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[List[str]] = Query(None),
    priority: Optional[List[str]] = Query(None),
    assignee_ids: Optional[List[int]] = Query(None),
    created_by: Optional[int] = Query(None),
    tags: Optional[List[str]] = Query(None),
    due_date_from: Optional[str] = Query(None),
    due_date_to: Optional[str] = Query(None),
    created_from: Optional[str] = Query(None),
    created_to: Optional[str] = Query(None),
    has_dependencies: Optional[bool] = Query(None),
    has_subtasks: Optional[bool] = Query(None),
    logic: str = Query("AND", pattern="^(AND|OR)$"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all tasks with optional filtering."""
    from datetime import datetime
    
    task_service = TaskService(db)
    auth_service = AuthService(db)
    
    # Build filter from query parameters
    task_filter = TaskFilter(
        status=[TaskStatus(s) for s in status] if status else None,
        priority=[TaskPriority(p) for p in priority] if priority else None,
        assignee_ids=assignee_ids,
        created_by=created_by,
        tags=tags,
        due_date_from=datetime.fromisoformat(due_date_from) if due_date_from else None,
        due_date_to=datetime.fromisoformat(due_date_to) if due_date_to else None,
        created_from=datetime.fromisoformat(created_from) if created_from else None,
        created_to=datetime.fromisoformat(created_to) if created_to else None,
        has_dependencies=has_dependencies,
        has_subtasks=has_subtasks,
        logic=logic
    )
    
    # Filter tasks
    tasks = task_service.filter_tasks(task_filter, skip, limit)
    
    # Filter by permissions
    accessible_tasks = []
    for task in tasks:
        if auth_service.can_access_task(current_user, task):
            accessible_tasks.append(task)
    
    return [task_service.task_to_response(task) for task in accessible_tasks]


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific task."""
    task_service = TaskService(db)
    auth_service = AuthService(db)
    
    task = task_service.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    if not auth_service.can_access_task(current_user, task):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this task"
        )
    
    return task_service.task_to_response(task)


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a task."""
    task_service = TaskService(db)
    auth_service = AuthService(db)
    
    task = task_service.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    if not auth_service.can_modify_task(current_user, task):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to modify this task"
        )
    
    updated_task = task_service.update_task(task_id, task_data)
    return task_service.task_to_response(updated_task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a task."""
    task_service = TaskService(db)
    auth_service = AuthService(db)
    
    task = task_service.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    if not auth_service.can_delete_task(current_user, task):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this task"
        )
    
    task_service.delete_task(task_id)
    return None


@router.put("/bulk-update", response_model=dict)
def bulk_update_tasks(
    bulk_update: BulkTaskUpdate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER])),
    db: Session = Depends(get_db)
):
    """Bulk update multiple tasks."""
    task_service = TaskService(db)
    auth_service = AuthService(db)
    
    # Check permissions for all tasks
    for task_id in bulk_update.task_ids:
        task = task_service.get_task(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found"
            )
        if not auth_service.can_modify_task(current_user, task):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions to modify task {task_id}"
            )
    
    updated_count = task_service.bulk_update_tasks(bulk_update)
    return {"updated_count": updated_count, "message": f"Successfully updated {updated_count} tasks"}


@router.post("/{task_id}/subtasks", response_model=SubtaskResponse, status_code=status.HTTP_201_CREATED)
def create_subtask(
    task_id: int,
    subtask_data: SubtaskCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a subtask for a task."""
    task_service = TaskService(db)
    auth_service = AuthService(db)
    
    task = task_service.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    if not auth_service.can_modify_task(current_user, task):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create subtasks for this task"
        )
    
    subtask = task_service.create_subtask(task_id, subtask_data)
    return task_service.subtask_to_response(subtask)


@router.get("/{task_id}/subtasks", response_model=List[SubtaskResponse])
def get_subtasks(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all subtasks for a task."""
    task_service = TaskService(db)
    auth_service = AuthService(db)
    
    task = task_service.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    if not auth_service.can_access_task(current_user, task):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this task"
        )
    
    subtasks = task_service.get_subtasks(task_id)
    return [task_service.subtask_to_response(subtask) for subtask in subtasks]


@router.get("/{task_id}/subtasks/{subtask_id}", response_model=SubtaskResponse)
def get_subtask(
    task_id: int,
    subtask_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific subtask."""
    task_service = TaskService(db)
    auth_service = AuthService(db)
    
    task = task_service.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    if not auth_service.can_access_task(current_user, task):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this task"
        )
    
    subtask = task_service.get_subtask(subtask_id)
    if not subtask:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subtask not found"
        )
    
    if subtask.parent_task_id != task_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subtask does not belong to this task"
        )
    
    return task_service.subtask_to_response(subtask)


@router.put("/{task_id}/subtasks/{subtask_id}", response_model=SubtaskResponse)
def update_subtask(
    task_id: int,
    subtask_id: int,
    subtask_data: SubtaskUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a subtask."""
    task_service = TaskService(db)
    auth_service = AuthService(db)
    
    task = task_service.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    if not auth_service.can_modify_task(current_user, task):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to modify this task"
        )
    
    subtask = task_service.get_subtask(subtask_id)
    if not subtask:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subtask not found"
        )
    
    if subtask.parent_task_id != task_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subtask does not belong to this task"
        )
    
    updated_subtask = task_service.update_subtask(subtask_id, subtask_data)
    return task_service.subtask_to_response(updated_subtask)


@router.delete("/{task_id}/subtasks/{subtask_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subtask(
    task_id: int,
    subtask_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a subtask."""
    task_service = TaskService(db)
    auth_service = AuthService(db)
    
    task = task_service.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    if not auth_service.can_modify_task(current_user, task):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to modify this task"
        )
    
    subtask = task_service.get_subtask(subtask_id)
    if not subtask:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subtask not found"
        )
    
    if subtask.parent_task_id != task_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subtask does not belong to this task"
        )
    
    task_service.delete_subtask(subtask_id)
    return None


@router.post("/{task_id}/dependencies", response_model=TaskDependencyResponse, status_code=status.HTTP_201_CREATED)
def create_dependency(
    task_id: int,
    dependency_data: TaskDependencyCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a task dependency."""
    task_service = TaskService(db)
    auth_service = AuthService(db)
    
    task = task_service.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    depends_on_task = task_service.get_task(dependency_data.depends_on_task_id)
    if not depends_on_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dependency task not found"
        )
    
    if not auth_service.can_modify_task(current_user, task):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to modify this task"
        )
    
    try:
        dependency = task_service.create_dependency(task_id, dependency_data)
        return task_service.dependency_to_response(dependency)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{task_id}/dependencies", response_model=List[TaskDependencyResponse])
def get_dependencies(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all dependencies for a task."""
    task_service = TaskService(db)
    auth_service = AuthService(db)
    
    task = task_service.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    if not auth_service.can_access_task(current_user, task):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this task"
        )
    
    dependencies = task_service.get_dependencies(task_id)
    return [task_service.dependency_to_response(dep) for dep in dependencies]


@router.delete("/{task_id}/dependencies/{dependency_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dependency(
    task_id: int,
    dependency_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a task dependency."""
    task_service = TaskService(db)
    auth_service = AuthService(db)
    
    task = task_service.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    if not auth_service.can_modify_task(current_user, task):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to modify this task"
        )
    
    if not task_service.delete_dependency(dependency_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dependency not found"
        )
    
    return None

