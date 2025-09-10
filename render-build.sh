#!/usr/bin/env bash
set -e

echo "Installing deps…"
pip install -r requirements.txt

echo "Running DB migrations…"
flask db upgrade

echo "Creating admin (idempotent)…"
python - <<'PY'
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
email = "admin@example.com"
pwd = "Admin123!"
u = User.query.filter_by(email=email).first()
if not u:
u = User(name="Admin", email=email, role="admin",
password_hash=generate_password_hash(pwd))
db.session.add(u)
db.session.commit()
print("Admin created:", email)
else:
print("Admin already exists")
PY
