# Fujitsu Incident & SLA Tracker

A Flask-based web application for managing **clients, incidents, and SLAs** (Service Level Agreements).
This project is designed to demonstrate database integration, authentication, and deployment readiness using **Flask, SQLAlchemy, and Gunicorn**.

---

## Features
-  User authentication (with role-based access: admin / user)
- Client management (add, edit, delete, view)
- Incident tracking (log incidents, update status, view history)
- Database migrations (Flask-Migrate + Alembic)
- Ready for deployment (Procfile, Gunicorn, requirements.txt)

---

## Tech Stack
- **Backend**: Flask (Python)
- **Database**: SQLite (local), PostgreSQL (production)
- **ORM**: SQLAlchemy
- **Authentication**: Flask-Login
- **Deployment**: Gunicorn + Render/Heroku

---

## Project Structure
