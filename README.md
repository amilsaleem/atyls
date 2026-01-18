Task Management API

This project is a RESTful Task Management API built using Python and FastAPI. It focuses on clean architecture, performance, and real-world product features commonly expected in modern task and project management systems.

What This API Does Well

Core Capabilities
Full CRUD operations for tasks with a well-structured data model
Authentication and authorization using JWT with role-based access (Admin, Manager, Member)
SQLAlchemy ORM with SQLite for quick setup (easily configurable for PostgreSQL)
Optimized queries with proper indexing for fast response times
Bulk task updates, allowing multiple tasks to be updated in a single request

Key Product Features
1. Advanced Task Filtering (AND / OR Logic)

Why this matters:
In real task management systems, users rarely search by a single field. They need flexibility—such as finding high-priority tasks assigned to a specific user that are overdue, or tasks marked urgent regardless of assignee. Supporting AND/OR logic makes the API far more practical and powerful.

What’s implemented:
Filtering by status, priority, assignee, due date, tags, and creation date
Support for complex AND / OR filter combinations
Efficient query construction using indexed database fields

2. Task Dependencies (Blocking Relationships)

Why this matters:
Task dependencies are essential for project planning. They help teams understand execution order and prevent work from starting before prerequisites are complete. This feature adds real project-management value to the system.

What’s implemented:
Define blocking relationships between tasks (e.g., Task A must be completed before Task B)
Fetch tasks along with their dependencies
Automatic detection of circular dependencies
Ability to filter tasks based on dependency status

Project Structure

```
Backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration settings
│   ├── database.py             # Database connection and session management
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py             # User model
│   │   └── task.py             # Task, Subtask, and related models
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py             # Authentication schemas
│   │   └── task.py             # Task schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py     # Authentication service
│   │   ├── task_service.py    # Task business logic
│   │   └── filter_service.py  # Advanced filtering logic
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base_repository.py # Base repository with OOP abstractions
│   │   ├── user_repository.py # User data access
│   │   └── task_repository.py # Task data access
│   └── api/
│       ├── __init__.py
│       ├── dependencies.py     # FastAPI dependencies
│       ├── routes/
│       │   ├── __init__.py
│       │   ├── auth.py         # Authentication routes
│       │   └── tasks.py        # Task routes
└── requirements.txt
```

Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

API documentation (Swagger UI) is available at `http://localhost:8000/docs`

API Endpoints

Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and get JWT token

Tasks
- `GET /tasks` - Get all tasks (with filtering support)
- `POST /tasks` - Create a new task
- `GET /tasks/{task_id}` - Get a specific task
- `PUT /tasks/{task_id}` - Update a task
- `DELETE /tasks/{task_id}` - Delete a task
- `PUT /tasks/bulk-update` - Update multiple tasks

Task Dependencies
- `POST /tasks/{task_id}/dependencies` - Add a dependency to a task
- `GET /tasks/{task_id}/dependencies` - Get all dependencies for a task
- `DELETE /tasks/{task_id}/dependencies/{dependency_id}` - Remove a dependency

Subtasks
- `POST /tasks/{task_id}/subtasks` - Create a subtask
- `GET /tasks/{task_id}/subtasks` - Get all subtasks for a task
- `GET /tasks/{task_id}/subtasks/{subtask_id}` - Get a specific subtask
- `PUT /tasks/{task_id}/subtasks/{subtask_id}` - Update a subtask
- `DELETE /tasks/{task_id}/subtasks/{subtask_id}` - Delete a subtask

Authentication

All endpoints except `/auth/register` and `/auth/login` require authentication. Include the JWT token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

Roles

- **Admin**: Full access to all operations
- **Manager**: Can create, update, and delete tasks, assign tasks to users
- **Member**: Can view and update assigned tasks, create tasks

Database

The application uses SQLite by default (for easy setup). To switch to PostgreSQL, update the database URL in `app/config.py`.

Design Decisions

1. **Object-Oriented Design**: Used repository pattern and service layer for separation of concerns
2. **Database**: SQLAlchemy ORM for database abstraction and easy migrations
3. **Authentication**: JWT tokens for stateless authentication
4. **Validation**: Pydantic models for request/response validation
5. **Performance**: Proper indexing on frequently queried fields, optimized queries

