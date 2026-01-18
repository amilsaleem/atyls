from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.task_repository import TaskRepository, SubtaskRepository
from app.repositories.user_repository import UserRepository
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
from app.models.task import Task, Subtask, TaskDependency, TaskAssignment, TaskTag
from app.models.user import User


class TaskService:
    """Service for task-related business logic."""
    
    def __init__(self, db: Session):
        """Initialize task service with database session."""
        self.task_repo = TaskRepository(db)
        self.subtask_repo = SubtaskRepository(db)
        self.user_repo = UserRepository(db)
        self.db = db
    
    def create_task(self, task_data: TaskCreate, created_by: int) -> Task:
        """Create a new task."""
        # Create task
        task = self.task_repo.create(
            title=task_data.title,
            description=task_data.description,
            status=task_data.status,
            priority=task_data.priority,
            due_date=task_data.due_date,
            created_by=created_by
        )
        
        # Add assignees
        if task_data.assignee_ids:
            self.task_repo.add_assignees(task.id, task_data.assignee_ids)
        
        # Add tags
        if task_data.tags:
            self.task_repo.add_tags(task.id, task_data.tags)
        
        return task
    
    def get_task(self, task_id: int) -> Optional[Task]:
        """Get a task by ID."""
        return self.task_repo.get_task_with_relations(task_id)
    
    def get_all_tasks(self, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get all tasks."""
        return self.task_repo.get_all_with_relations(skip, limit)
    
    def filter_tasks(self, task_filter: TaskFilter, skip: int = 0, limit: int = 100) -> List[Task]:
        """Filter tasks based on criteria."""
        return self.task_repo.filter_tasks(task_filter, skip, limit)
    
    def update_task(self, task_id: int, task_data: TaskUpdate) -> Optional[Task]:
        """Update a task."""
        # Prepare update data
        update_dict = {}
        if task_data.title is not None:
            update_dict["title"] = task_data.title
        if task_data.description is not None:
            update_dict["description"] = task_data.description
        if task_data.status is not None:
            update_dict["status"] = task_data.status
        if task_data.priority is not None:
            update_dict["priority"] = task_data.priority
        if task_data.due_date is not None:
            update_dict["due_date"] = task_data.due_date
        
        # Update task
        task = self.task_repo.update(task_id, **update_dict)
        
        # Update assignees if provided
        if task_data.assignee_ids is not None:
            self.task_repo.add_assignees(task_id, task_data.assignee_ids)
        
        # Update tags if provided
        if task_data.tags is not None:
            self.task_repo.add_tags(task_id, task_data.tags)
        
        return self.task_repo.get_task_with_relations(task_id)
    
    def bulk_update_tasks(self, bulk_update: BulkTaskUpdate) -> int:
        """Bulk update multiple tasks."""
        # Prepare update data
        update_dict = {}
        if bulk_update.update_data.title is not None:
            update_dict["title"] = bulk_update.update_data.title
        if bulk_update.update_data.description is not None:
            update_dict["description"] = bulk_update.update_data.description
        if bulk_update.update_data.status is not None:
            update_dict["status"] = bulk_update.update_data.status
        if bulk_update.update_data.priority is not None:
            update_dict["priority"] = bulk_update.update_data.priority
        if bulk_update.update_data.due_date is not None:
            update_dict["due_date"] = bulk_update.update_data.due_date
        
        # Perform bulk update
        updated_count = self.task_repo.bulk_update(bulk_update.task_ids, update_dict)
        
        # Handle assignees and tags if provided
        if bulk_update.update_data.assignee_ids is not None:
            for task_id in bulk_update.task_ids:
                self.task_repo.add_assignees(task_id, bulk_update.update_data.assignee_ids)
        
        if bulk_update.update_data.tags is not None:
            for task_id in bulk_update.task_ids:
                self.task_repo.add_tags(task_id, bulk_update.update_data.tags)
        
        return updated_count
    
    def delete_task(self, task_id: int) -> bool:
        """Delete a task."""
        return self.task_repo.delete(task_id)
    
    def create_subtask(self, task_id: int, subtask_data: SubtaskCreate) -> Subtask:
        """Create a subtask."""
        return self.subtask_repo.create(
            parent_task_id=task_id,
            title=subtask_data.title,
            description=subtask_data.description,
            status=subtask_data.status,
            priority=subtask_data.priority,
            due_date=subtask_data.due_date
        )
    
    def get_subtask(self, subtask_id: int) -> Optional[Subtask]:
        """Get a subtask by ID."""
        return self.subtask_repo.get_by_id(subtask_id)
    
    def get_subtasks(self, task_id: int) -> List[Subtask]:
        """Get all subtasks for a task."""
        return self.subtask_repo.get_by_parent_task(task_id)
    
    def update_subtask(self, subtask_id: int, subtask_data: SubtaskUpdate) -> Optional[Subtask]:
        """Update a subtask."""
        # Prepare update data
        update_dict = {}
        if subtask_data.title is not None:
            update_dict["title"] = subtask_data.title
        if subtask_data.description is not None:
            update_dict["description"] = subtask_data.description
        if subtask_data.status is not None:
            update_dict["status"] = subtask_data.status
        if subtask_data.priority is not None:
            update_dict["priority"] = subtask_data.priority
        if subtask_data.due_date is not None:
            update_dict["due_date"] = subtask_data.due_date
        
        # Update subtask
        return self.subtask_repo.update(subtask_id, **update_dict)
    
    def delete_subtask(self, subtask_id: int) -> bool:
        """Delete a subtask."""
        return self.subtask_repo.delete(subtask_id)
    
    def create_dependency(self, task_id: int, dependency_data: TaskDependencyCreate) -> TaskDependency:
        """Create a task dependency."""
        return self.task_repo.create_dependency(task_id, dependency_data.depends_on_task_id)
    
    def get_dependencies(self, task_id: int) -> List[TaskDependency]:
        """Get all dependencies for a task."""
        return self.task_repo.get_dependencies(task_id)
    
    def delete_dependency(self, dependency_id: int) -> bool:
        """Delete a task dependency."""
        return self.task_repo.delete_dependency(dependency_id)
    
    @staticmethod
    def task_to_response(task: Task) -> TaskResponse:
        """Convert Task model to TaskResponse schema."""
        assignee_ids = [assignment.user_id for assignment in task.assignments]
        tags = [tag.tag for tag in task.tags]
        
        return TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            due_date=task.due_date,
            created_at=task.created_at,
            updated_at=task.updated_at,
            created_by=task.created_by,
            assignees=assignee_ids,
            tags=tags,
            subtask_count=len(task.subtasks),
            dependency_count=len(task.dependencies)
        )
    
    @staticmethod
    def subtask_to_response(subtask: Subtask) -> SubtaskResponse:
        """Convert Subtask model to SubtaskResponse schema."""
        return SubtaskResponse(
            id=subtask.id,
            parent_task_id=subtask.parent_task_id,
            title=subtask.title,
            description=subtask.description,
            status=subtask.status,
            priority=subtask.priority,
            due_date=subtask.due_date,
            created_at=subtask.created_at,
            updated_at=subtask.updated_at
        )
    
    @staticmethod
    def dependency_to_response(dependency: TaskDependency) -> TaskDependencyResponse:
        """Convert TaskDependency model to TaskDependencyResponse schema."""
        return TaskDependencyResponse(
            id=dependency.id,
            task_id=dependency.task_id,
            depends_on_task_id=dependency.depends_on_task_id,
            created_at=dependency.created_at
        )

