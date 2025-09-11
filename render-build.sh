#!/usr/bin/env bash
set -euo pipefail

echo "Installing deps..."
pip install -r requirements.txt

echo "Running DB migrations..."
# Make sure Flask knows where the app is for CLI commands
export FLASK_APP=wsgi:app
flask db upgrade

echo "Creating admin (idempotent)..."
python <<'PY'
from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    email = "admin@example.com"
    password = "Admin123!"

    u = User.query.filter_by(email=email).first()
    if u:
        print("Admin already exists:", email)
    else:
        u = User(
            name="Admin",
            email=email,
            role="admin",
            password_hash=generate_password_hash(password),
        )
        db.session.add(u)
        db.session.commit()
        print("Admin created:", email)
PY

echo "Build script finished."
