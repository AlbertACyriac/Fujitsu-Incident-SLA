from datetime import datetime
from flask_login import UserMixin
from app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="regular")  # admin|regular
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # relationships
    incidents = db.relationship("Incident", backref="creator", lazy=True)

    # helpers
    def set_password(self, raw_password: str):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)

    @property
    def is_admin(self) -> bool:
        return (self.role or "").lower() == "admin"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Client(db.Model):
    __tablename__ = "clients"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    sector = db.Column(db.String(120))
    contact_email = db.Column(db.String(120))
    incidents = db.relationship("Incident", backref="client", lazy=True)

class SLA(db.Model):
    __tablename__ = "slas"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    target_response_mins = db.Column(db.Integer, nullable=False)
    target_resolve_mins = db.Column(db.Integer, nullable=False)
    incidents = db.relationship("Incident", backref="sla", lazy=True)

class Incident(db.Model):
    __tablename__ = "incidents"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(db.String(10), nullable=False)   # Low|Medium|High
    status = db.Column(db.String(20), default="Open")     # Open|In-Progress|Resolved|Closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    sla_id = db.Column(db.Integer, db.ForeignKey("slas.id"), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

