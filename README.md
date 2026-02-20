# KanMind Backend

Django REST API for a Kanban board application.

## Installation

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Setup

**1. Configure environment variables:**

```bash
cp .env.template .env
```

Then edit `.env` and set your values:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
```

**2. Run database migrations and start the server:**

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Technologies

- Python 3.14
- Django 5.2
- Django REST Framework 3.16.1
- SQLite

## API Endpoints

### Authentication

- `POST /api/registration/` - User registration
- `POST /api/login/` - User login
- `POST /api/logout/` - User logout
- `GET /api/profile/` - User profile
- `GET /api/email-check/?email=` - Check if email exists
- `GET /api/users/me/` - Current user data

### Boards

- `GET /api/boards/` - List boards
- `POST /api/boards/` - Create board
- `GET /api/boards/<id>/` - Board detail
- `PUT /api/boards/<id>/` - Update board
- `DELETE /api/boards/<id>/` - Delete board

### Tasks

- `GET /api/tasks/` - List tasks
- `POST /api/tasks/` - Create task
- `GET /api/tasks/<id>/` - Task detail
- `PUT /api/tasks/<id>/` - Update task
- `DELETE /api/tasks/<id>/` - Delete task
- `GET /api/tasks/assigned-to-me/` - Tasks assigned to current user
- `GET /api/tasks/reviewing/` - Tasks in review status

### Comments

- `GET /api/comments/` - List comments
- `POST /api/comments/` - Create comment
- `GET /api/tasks/<id>/comments/` - List task comments
- `POST /api/tasks/<id>/comments/` - Create task comment
- `DELETE /api/tasks/<task_id>/comments/<comment_id>/` - Delete comment

### Users

- `GET /api/users/` - List all users

## Token Usage

This project uses Token Authentication. Include the token in the
Authorization header:

```text
Authorization: Token <your-token>
```

## Frontend

The frontend code is available in a separate repository:
[Developer-Akademie-Backendkurs/project.KanMind](https://github.com/Developer-Akademie-Backendkurs/project.KanMind)

## Author

Mohamed Touzani - Developer Akademie
