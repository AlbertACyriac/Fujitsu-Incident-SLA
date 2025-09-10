#!/usr/bin/env bash
set -euo pipefail

echo "Installing deps…"
pip install -r requirements.txt

echo "Running DB migrations…"
# Render sets DATABASE_URL; Flask picks it up in create_app()
# Ensure Flask knows where the app is:
export FLASK_APP=wsgi.py
flask db upgrade

echo "Creating admin (idempotent)…"
python - <<'PY'
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
email = "admin@example.com"
password = "Admin123!"
user = User.query.filter_by(email=email).first()
if user:
print("Admin already exists:", email)
else:
user = User(
name="Admin",
email=email,
role="admin",
password_hash=generate_password_hash(password),
)
db.session.add(user)
db.session.commit()
print("Admin created:", email)
PY

echo "Build script finished."
