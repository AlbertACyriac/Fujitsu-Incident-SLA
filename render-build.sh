#!/usr/bin/env bash
set -e

# 1) Install deps
pip install -r requirements.txt

# 2) Apply migrations on the production DB
flask db upgrade

# 3) Ensure an admin user exists (safe to re-run)
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
db.session.add(u); db.session.commit()
print("Admin created:", email)
else:
print("Admin already exists:", email)
PY

