# Student Management System

A Django-based web application for managing student records.

## Features

- View all students
- Add new students
- Edit existing students
- Delete students
- Search students by name or course
- Sort students by name, age, or course
- Pagination for better navigation

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/SmartClass.git
cd SmartClass
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install django
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

7. Access the application at `http://127.0.0.1:8000/`

## Project Structure

```
SmartClass/
├── manage.py
├── SmartClass/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
└── students/
    ├── migrations/
    ├── templates/
    │   └── students/
    │       ├── base.html
    │       ├── home.html
    │       ├── add.html
    │       └── update.html
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── models.py
    ├── tests.py
    └── views.py
```

## Technologies Used

- Django 5.2
- SQLite
- HTML/CSS
- Bootstrap (for styling)

## License

This project is licensed under the MIT License. 