#!/usr/bin/env bash
set -euo pipefail

echo "==> Release step started"
python -V
echo "==> FLASK_APP=${FLASK_APP:-not set}"
echo "==> FLASK_ENV=${FLASK_ENV:-not set}"

if [[ -n "${DATABASE_URL:-}" ]]; then
echo "==> DATABASE_URL present (masked)"
else
echo "!! DATABASE_URL is NOT set"
fi

echo "==> Running Alembic migrations (flask db upgrade)…"
flask db upgrade
echo "==> Migrations complete."

echo "==> Creating admin user if missing…"
python - <<'PYCODE'
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash as gph

app = create_app()
with app.app_context():
email = "admin@example.com"
pw = "password123"
u = User.query.filter_by(email=email).first()
if not u:
u = User(name="Admin", email=email, role="admin",
password_hash=gph(pw))
db.session.add(u)
db.session.commit()
print(f"Admin created: {email} / {pw}")
else:
print(f"User already exists: {email}")
PYCODE

echo "==> Release step finished OK."
