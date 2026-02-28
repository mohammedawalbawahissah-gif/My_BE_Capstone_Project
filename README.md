# Neomat Care – ALX Backend Capstone Project

## Project Title
Neomat Care – Maternal Emergency Referral System

---

## Project Description

Neomat Care is a backend system built with Django as part of the ALX Backend Engineering Capstone Project.

The system is designed to manage patient records, obstetric emergency cases based on risk assessment, and quick referral processes within the rural healthcare system to help fight maternal and neonatal deaths in Sub-Saharan Africa. It provides secure authentication, structured database management, and organized clinical workflows.

This project demonstrates the ability to design, structure, and implement a production-ready backend application using industry best practices.

---

## Problem Statement

Healthcare facilities, especially in rural areas in Sub-Saharan Africa often struggle with:

- Poor patient record tracking
- Manual emergency case documentation
- Inefficient referral management
- Delayed response time to obstetric emergencies

These issues lead to:
- Data inconsistency
- Delayed patient care
- Administrative inefficiencies
- High maternal and neonatal mortality (70% of the Global incidence)

---

## Proposed Solution

Neomat Care provides:

- A structured database for patient records
- Efficient emergency case management
- Quick referral tracking
- Reduced response time 
- Secure authentication system
- Organised Django-based architecture

The system ensures reliable data storage, structured workflows, and secure access control.

---

## System Architecture

The project follows Django’s MVT (Model-View-Template) architecture:

- **Models** → Database schema and data relationships
- **Views** → Business logic and request handling
- **Templates** → UI rendering
- **URLs** → Route mapping

Database: PostgreSQL  
Backend Framework: Django 6.x  
Language: Python 3.x  

---

## Core Features Implemented

### Authentication
- User registration
- Login/logout functionality
- Authenticated route protection
- Conditional template rendering

---

### Patient Management (CRUD)
- Create patient records
- View patient list
- View detailed patient profile
- Update patient information
- Delete patient with confirmation

---

### Emergency Management
- Register emergency cases
- View emergency records
- Dashboard integration

---

### Referral Management
- Create referrals
- View referral list
- Track referral details

---

### Template System
- Base layout using `base.html`
- Template inheritance with `{% block %}`
- Reusable navbar
- Static file management
- Clean UI structure

---

## Database Design

The system uses relational database modeling with:

- Structured patient data
- Linked emergency cases
- Referral tracking models
- Proper foreign key relationships
- Django ORM for database interaction

Migrations were properly managed using:

```
python manage.py makemigrations
python manage.py migrate
```

---

## Backend Concepts Demonstrated

This project demonstrates:

- Django project structuring
- URL routing & namespacing
- Model design & relationships
- ORM usage
- Template inheritance
- Static file handling
- PostgreSQL configuration
- Environment isolation with virtual environments
- Git version control best practices
- Repository cleanup using `.gitignore`
- Debugging template and migration errors

---

## Repository Management

- Implemented proper `.gitignore`
- Removed unnecessary tracked files (e.g., `venv/`)
- Clean commit history
- Organized project structure

---

## ⚙️ Installation & Setup

### Clone Repository
```
git clone <repository-url>
cd neomat_care
```

### Create Virtual Environment
```
python -m venv venv
```

Activate:

Windows:
```
venv\Scripts\activate
```

Mac/Linux:
```
source venv/bin/activate
```

---

### Install Dependencies
```
pip install -r requirements.txt
```

---

### Configure Database

Update `settings.py` with PostgreSQL credentials.

---

### Apply Migrations
```
python manage.py makemigrations
python manage.py migrate
```

---

### Run Development Server
```
python manage.py runserver
```

Access:
```
http://127.0.0.1:8000/
```

---

## Testing Approach

- Manual functional testing of all routes
- CRUD validation for patients
- Authentication access testing
- Database integrity verification

---

## Future Improvements

- REST API integration (Django REST Framework)
- Role-based access control
- API documentation
- Unit testing
- Docker containerization
- Deployment to cloud platform
- Create a mobile app
- Build neomat.ai, the apps AI model for risk assessment
- Introduce a Telemedicine feature

---

## Author

Mohammed Awal Bawah Issah  
ALX Backend Engineering Program  
Backend Developer | Medical Laboratory Scientist | Medical Student

---

## Acknowledgment

This project was developed as the final capstone for the ALX Backend Engineering Program, demonstrating backend system design, implementation, and best practices.

## License

This project was developed for academic and portfolio purposes.
