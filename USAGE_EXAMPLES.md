# API Usage Examples

## Authentication

### Register a new user
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepassword123",
    "role": "member"
  }'
```

### Login

**Option 1: Using JSON (Recommended - Easier to use)**
```bash
curl -X POST "http://localhost:8000/auth/login/json" \
  -H "Content-Type: application/json" \
  -d '{"username": "john_doe", "password": "securepassword123"}'
```

**PowerShell:**
```powershell
curl.exe -X POST "http://localhost:8000/auth/login/json" -H "Content-Type: application/json" -d '{\"username\": \"john_doe\", \"password\": \"securepassword123\"}'
```

**Option 2: Using OAuth2 Form Data (Standard OAuth2 format)**
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john_doe&password=securepassword123"
```

**PowerShell:**
```powershell
curl.exe -X POST "http://localhost:8000/auth/login" -H "Content-Type: application/x-www-form-urlencoded" -d "username=john_doe&password=securepassword123"
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

## Tasks

### Create a task
```bash
curl -X POST "http://localhost:8000/tasks" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Implement user authentication",
    "description": "Add JWT-based authentication to the API",
    "status": "todo",
    "priority": "high",
    "due_date": "2024-12-31T23:59:59",
    "assignee_ids": [1, 2],
    "tags": ["backend", "security", "urgent"]
  }'
```

### Get all tasks with filtering (AND logic)
```bash
curl -X GET "http://localhost:8000/tasks?status=todo&priority=high&logic=AND" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get tasks with OR logic
```bash
curl -X GET "http://localhost:8000/tasks?status=todo&status=in_progress&priority=urgent&logic=OR" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Filter by assignee and tags
```bash
curl -X GET "http://localhost:8000/tasks?assignee_ids=1&assignee_ids=2&tags=urgent&logic=AND" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Filter by date range
```bash
curl -X GET "http://localhost:8000/tasks?due_date_from=2024-01-01T00:00:00&due_date_to=2024-12-31T23:59:59" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Update a task
```bash
curl -X PUT "http://localhost:8000/tasks/1" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress",
    "priority": "urgent"
  }'
```

### Bulk update tasks
```bash
curl -X PUT "http://localhost:8000/tasks/bulk-update" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task_ids": [1, 2, 3],
    "update_data": {
      "status": "completed",
      "priority": "low"
    }
  }'
```

## Task Dependencies

### Create a dependency (Task 2 depends on Task 1)
```bash
curl -X POST "http://localhost:8000/tasks/2/dependencies" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "depends_on_task_id": 1
  }'
```

### Get all dependencies for a task
```bash
curl -X GET "http://localhost:8000/tasks/2/dependencies" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Delete a dependency
```bash
curl -X DELETE "http://localhost:8000/tasks/2/dependencies/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Subtasks

### Create a subtask
```bash
curl -X POST "http://localhost:8000/tasks/1/subtasks" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Design database schema",
    "description": "Create ER diagram",
    "status": "todo",
    "priority": "medium"
  }'
```

### Get all subtasks for a task
```bash
curl -X GET "http://localhost:8000/tasks/1/subtasks" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get a specific subtask
```bash
curl -X GET "http://localhost:8000/tasks/1/subtasks/5" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Update a subtask
```bash
curl -X PUT "http://localhost:8000/tasks/1/subtasks/5" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress",
    "priority": "high"
  }'
```

### Delete a subtask
```bash
curl -X DELETE "http://localhost:8000/tasks/1/subtasks/5" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Filtering Examples

### Complex filtering with multiple criteria
```bash
# Find high or urgent priority tasks assigned to user 1 or 2, with tag "backend", due in 2024
curl -X GET "http://localhost:8000/tasks?priority=high&priority=urgent&assignee_ids=1&assignee_ids=2&tags=backend&due_date_from=2024-01-01T00:00:00&due_date_to=2024-12-31T23:59:59&logic=AND" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Filter tasks with dependencies
```bash
# Find tasks that have dependencies
curl -X GET "http://localhost:8000/tasks?has_dependencies=true" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Find tasks without dependencies
curl -X GET "http://localhost:8000/tasks?has_dependencies=false" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Filter tasks with subtasks
```bash
# Find tasks that have subtasks
curl -X GET "http://localhost:8000/tasks?has_subtasks=true" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

