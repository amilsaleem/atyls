from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from datetime import datetime
from app.models.task import Task, Subtask, TaskDependency, TaskAssignment, TaskTag, TaskStatus, TaskPriority
from app.repositories.base_repository import BaseRepository
from app.schemas.task import TaskFilter


class TaskRepository(BaseRepository[Task]):
    """Repository for Task model operations."""
    
    def __init__(self, db: Session):
        super().__init__(Task, db)
    
    def get_by_field(self, field_name: str, value: any) -> Optional[Task]:
        """Get task by a specific field."""
        return self.db.query(Task).filter(getattr(Task, field_name) == value).first()
    
    def get_task_with_relations(self, task_id: int) -> Optional[Task]:
        """Get task with all related data loaded."""
        return (
            self.db.query(Task)
            .options(
                joinedload(Task.assignments).joinedload(TaskAssignment.user),
                joinedload(Task.subtasks),
                joinedload(Task.dependencies).joinedload(TaskDependency.depends_on_task),
                joinedload(Task.tags)
            )
            .filter(Task.id == task_id)
            .first()
        )
    
    def get_all_with_relations(self, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get all tasks with relations loaded."""
        return (
            self.db.query(Task)
            .options(
                joinedload(Task.assignments).joinedload(TaskAssignment.user),
                joinedload(Task.subtasks),
                joinedload(Task.dependencies).joinedload(TaskDependency.depends_on_task),
                joinedload(Task.tags)
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def filter_tasks(self, task_filter: TaskFilter, skip: int = 0, limit: int = 100) -> List[Task]:
        """Filter tasks based on TaskFilter criteria with AND/OR logic."""
        query = self.db.query(Task)
        
        conditions = []
        
        # Build filter conditions
        if task_filter.status:
            status_condition = Task.status.in_(task_filter.status)
            conditions.append(status_condition)
        
        if task_filter.priority:
            priority_condition = Task.priority.in_(task_filter.priority)
            conditions.append(priority_condition)
        
        if task_filter.created_by:
            created_by_condition = Task.created_by == task_filter.created_by
            conditions.append(created_by_condition)
        
        if task_filter.due_date_from:
            due_date_from_condition = Task.due_date >= task_filter.due_date_from
            conditions.append(due_date_from_condition)
        
        if task_filter.due_date_to:
            due_date_to_condition = Task.due_date <= task_filter.due_date_to
            conditions.append(due_date_to_condition)
        
        if task_filter.created_from:
            created_from_condition = Task.created_at >= task_filter.created_from
            conditions.append(created_from_condition)
        
        if task_filter.created_to:
            created_to_condition = Task.created_at <= task_filter.created_to
            conditions.append(created_to_condition)
        
        if task_filter.assignee_ids:
            # Filter by assignees using EXISTS subquery
            assignee_subquery = (
                self.db.query(TaskAssignment.task_id)
                .filter(TaskAssignment.user_id.in_(task_filter.assignee_ids))
                .filter(TaskAssignment.task_id == Task.id)
                .exists()
            )
            conditions.append(assignee_subquery)
        
        if task_filter.tags:
            # Filter by tags using EXISTS subquery
            tag_subquery = (
                self.db.query(TaskTag.task_id)
                .filter(TaskTag.tag.in_(task_filter.tags))
                .filter(TaskTag.task_id == Task.id)
                .exists()
            )
            conditions.append(tag_subquery)
        
        if task_filter.has_dependencies is not None:
            # Filter by presence of dependencies using EXISTS
            dep_subquery = (
                self.db.query(TaskDependency.task_id)
                .filter(TaskDependency.task_id == Task.id)
                .exists()
            )
            if task_filter.has_dependencies:
                conditions.append(dep_subquery)
            else:
                conditions.append(~dep_subquery)
        
        if task_filter.has_subtasks is not None:
            # Filter by presence of subtasks using EXISTS
            subtask_subquery = (
                self.db.query(Subtask.parent_task_id)
                .filter(Subtask.parent_task_id == Task.id)
                .exists()
            )
            if task_filter.has_subtasks:
                conditions.append(subtask_subquery)
            else:
                conditions.append(~subtask_subquery)
        
        # Apply logic (AND or OR)
        if conditions:
            if task_filter.logic.upper() == "OR":
                query = query.filter(or_(*conditions))
            else:  # Default to AND
                query = query.filter(and_(*conditions))
        
        return query.options(
            joinedload(Task.assignments).joinedload(TaskAssignment.user),
            joinedload(Task.subtasks),
            joinedload(Task.dependencies).joinedload(TaskDependency.depends_on_task),
            joinedload(Task.tags)
        ).offset(skip).limit(limit).all()
    
    def bulk_update(self, task_ids: List[int], update_data: Dict[str, Any]) -> int:
        """Bulk update multiple tasks."""
        updated_count = (
            self.db.query(Task)
            .filter(Task.id.in_(task_ids))
            .update(update_data, synchronize_session=False)
        )
        self.db.commit()
        return updated_count
    
    def add_assignees(self, task_id: int, user_ids: List[int]) -> Task:
        """Add assignees to a task."""
        task = self.get_by_id(task_id)
        if task:
            # Remove existing assignments
            self.db.query(TaskAssignment).filter(TaskAssignment.task_id == task_id).delete()
            # Add new assignments
            for user_id in user_ids:
                assignment = TaskAssignment(task_id=task_id, user_id=user_id)
                self.db.add(assignment)
            self.db.commit()
            self.db.refresh(task)
        return task
    
    def add_tags(self, task_id: int, tags: List[str]) -> Task:
        """Add tags to a task."""
        task = self.get_by_id(task_id)
        if task:
            # Remove existing tags
            self.db.query(TaskTag).filter(TaskTag.task_id == task_id).delete()
            # Add new tags
            for tag in tags:
                task_tag = TaskTag(task_id=task_id, tag=tag)
                self.db.add(task_tag)
            self.db.commit()
            self.db.refresh(task)
        return task
    
    def create_dependency(self, task_id: int, depends_on_task_id: int) -> Optional[TaskDependency]:
        """Create a task dependency."""
        # Check for circular dependencies
        if self._has_circular_dependency(task_id, depends_on_task_id):
            raise ValueError("Circular dependency detected")
        
        dependency = TaskDependency(
            task_id=task_id,
            depends_on_task_id=depends_on_task_id
        )
        self.db.add(dependency)
        self.db.commit()
        self.db.refresh(dependency)
        return dependency
    
    def _has_circular_dependency(self, task_id: int, depends_on_task_id: int) -> bool:
        """Check if adding a dependency would create a circular reference."""
        # If the task we depend on depends on us (directly or indirectly), it's circular
        visited = set()
        to_check = [depends_on_task_id]
        
        while to_check:
            current = to_check.pop()
            if current == task_id:
                return True
            if current in visited:
                continue
            visited.add(current)
            
            # Get all tasks that current task depends on
            dependencies = (
                self.db.query(TaskDependency.depends_on_task_id)
                .filter(TaskDependency.task_id == current)
                .all()
            )
            to_check.extend([dep[0] for dep in dependencies])
        
        return False
    
    def get_dependencies(self, task_id: int) -> List[TaskDependency]:
        """Get all dependencies for a task."""
        return (
            self.db.query(TaskDependency)
            .options(joinedload(TaskDependency.depends_on_task))
            .filter(TaskDependency.task_id == task_id)
            .all()
        )
    
    def delete_dependency(self, dependency_id: int) -> bool:
        """Delete a task dependency."""
        dependency = self.db.query(TaskDependency).filter(TaskDependency.id == dependency_id).first()
        if dependency:
            self.db.delete(dependency)
            self.db.commit()
            return True
        return False


class SubtaskRepository(BaseRepository[Subtask]):
    """Repository for Subtask model operations."""
    
    def __init__(self, db: Session):
        super().__init__(Subtask, db)
    
    def get_by_field(self, field_name: str, value: any) -> Optional[Subtask]:
        """Get subtask by a specific field."""
        return self.db.query(Subtask).filter(getattr(Subtask, field_name) == value).first()
    
    def get_by_parent_task(self, parent_task_id: int) -> List[Subtask]:
        """Get all subtasks for a parent task."""
        return self.filter_by(parent_task_id=parent_task_id)

