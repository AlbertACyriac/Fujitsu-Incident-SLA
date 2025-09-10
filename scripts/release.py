# scripts/release.py
import os
from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
# Run DB migrations
from flask_migrate import upgrade
upgrade()

# Create admin once
email = os.environ.get("ADMIN_EMAIL", "admin@example.com")
password = os.environ.get("ADMIN_PASSWORD", "Admin123!")
admin = User.query.filter_by(email=email).first()
if not admin:
admin = User(
name="Admin",
email=email,
role="admin",
password_hash=generate_password_hash(password),
)
db.session.add(admin)
db.session.commit()
print("Admin created:", email)
else:
print("Admin already exists:", email)
