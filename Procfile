release: FLASK_APP=run.py flask db upgrade && flask create-admin "admin@example.com" "Admin123!"
web: gunicorn wsgi:app
