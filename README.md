Student Management System
A Django-based web application for managing student records.

1. INTRODUCTION  
The Smart Classroom Management System is a web application developed using Django that allows students, teachers, and school management to interact through a centralized system. Each user has access to different functionalities based on their role. The system is designed to digitize classroom workflows like attendance marking, assignment submissions, results, and scheduling. 
Django's Model-View-Template (MVT) architecture allowed us to keep the project modular and easy to scale. 

  
2. OBJECTIVE  
   To build a role-based smart classroom system using Django. 
   To manage data such as attendance, assignments, class schedules, and student performance. 
   To implement full CRUD operations using Django's ORM and SQLite, Object Oriented programming  
   To gain practical experience with backend logic, frontend rendering, and database management. 

 
3. PROPOSED WORK   
The project provides a login portal for three types of users: 
   Students can check their class schedules, view assignments, results, and deposit fees. 
   Teachers can mark attendance, give assignments, and enter student marks, view schedules. 
   School Management can manage classes, schedules, and user roles (add/delete/modify). 
We used Object-Oriented Programming (OOP) to structure our models and views. Django’s in-built authentication and admin panel helped manage users and data securely and efficiently. 


4. Installation
Clone the repository:
git clone https://github.com/aravmahind/SmartClass.git
cd SmartClass

Install dependencies:
pip install django

Run migrations:
python manage.py migrate

Create a superuser:
python manage.py createsuperuser

Run the development server:
python manage.py runserver
Access the application at http://127.0.0.1:8000/


5.	TOOLS & TECHNOLOGIES USED  
•  Programming Language: Python 
•  Framework: Django 
•	Database: SQLite (default DB for Django projects) 
•	Frontend: HTML, CSS 
•	Backend Architecture: Django MVT (Model-View-Template) 
•	Development Tools: Visual Studio Code 
•	Version Control: Git & GitHub
