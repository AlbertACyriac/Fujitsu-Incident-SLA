#!/usr/bin/env bash
set -e

echo "Installing deps…"
pip install -r requirements.txt

echo "Running DB migrations…"
# Make sure Flask knows where the app factory is
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
u = User(name="Admin", email=email, role="admin",
password_hash=generate_password_hash(password))
db.session.add(u)
db.session.commit()
print("Admin created:", email)
PY
chmod +x render-build.sh
git add render-build.sh
git commit -m "Recreate render-build.sh correctly"
git push origin main
BASG
