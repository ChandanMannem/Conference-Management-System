# Conference-Management-System
Conferenece Management System

step 1: Pull the repo

step 2: Run below commands in the root directory which is coference-management-system in your local

    1. Create seperate environment (eg: Django_SSDI) in python for this project.
    
    2. To activate virtual environmeent
       venv\Django_SSDI(Your environment Name)\Scripts\activate
     
    3. Install django 
       pip install django
       
    4. install postgres db
       pip install psycopg2
       
    5. Create superuser for django
       username: admin
       password: password
       email : admin@sampleemail.com
       
    6. Install postgres and create the following database with PG Admin 4.  
        db name: 'CMS_Database',
        username: 'postgres',
        password: 'admin',
        host : 'localhost',
        
    7. Additional information to create the django project and application.
    
        Below commands works only with python environment where django is installed
        
        To Start Project:
        django-admin startproject ProjectName
        
        To Start Application:
        1. Navigate inside the project upto manage.py
        2. python manage.py startapp ApplicationName
        
     
step 3: Create models in django and make migrations by running below commands in project folder
    python manage.py migrate

    python manage.py makemigrations ApplicationName

    python manage.py sqlmigrate api 0001 (0001 is the prefix of _initial.py file create in migration folder of the application)
    
    python manage.py migrate
    
 step 4: Finally, to run django server use command.
 
    python mange.py runserver
