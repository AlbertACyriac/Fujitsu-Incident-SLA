#!/usr/bin/env bash
set -euo pipefail

echo "===== Install deps ====="
pip install -r requirements.txt

echo "===== Run DB migrations ====="
flask db upgrade

echo "===== Create admin user (idempotent) ====="
python - <<'PY'
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
email = "admin@example.com"
pwd = "Admin123!"
user = User.query.filter_by(email=email).first()
if not user:
user = User(
name="Admin",
email=email,
role="admin",
password_hash=generate_password_hash(pwd)
)
db.session.add(user)
db.session.commit()
print("Admin created:", email, "password:", pwd)
else:
print("User already exists:", email)
PY

echo "===== build step finished ====="
