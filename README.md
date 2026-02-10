# KanMind Backend

Django REST API für Kanban Board Anwendung.

## Installation
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Setup
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Technologien

- Django 6.0.1
- Django REST Framework 3.16.1
- SQLite

## API Endpoints

- `/api/boards/` - Board Management
- `/api/tasks/` - Task Management
- `/api/comments/` - Kommentare
- `/api/registration/` - User Registrierung
- `/api/login/` - User Login

## Frontend

Der zugehörige Frontend-Code ist in einem separaten Repository verfügbar:
https://github.com/Developer-Akademie-Backendkurs/project.KanMind

## Autor

Mohamed Touzani - Developer Akademie