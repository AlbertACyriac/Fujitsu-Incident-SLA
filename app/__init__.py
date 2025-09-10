# app/__init__.py
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# --- extensions (one global instance each) ---
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

# where Flask-Login should redirect when a login is required
login_manager.login_view = "auth.login"


def create_app() -> Flask:
    app = Flask(__name__)

    # ---- configuration (env-first, with safe defaults) ----
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-key")

    db_url = os.environ.get("DATABASE_URL", "sqlite:///fujitsu_incident.db")
    # Render/Railway sometimes provide the old postgres:// scheme
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # ---- init extensions ----
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Import models so Alembic (migrations) sees them
    from app import models  # noqa: F401

    # ---- blueprints ----
    # auth
    from app.auth.routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    # CRUD areas
    from app.clients.routes import clients_bp
    from app.slas.routes import slas_bp
    from app.incidents.routes import incidents_bp
    app.register_blueprint(clients_bp,   url_prefix="/clients")
    app.register_blueprint(slas_bp,      url_prefix="/slas")
    app.register_blueprint(incidents_bp, url_prefix="/incidents")

    # optional main/home blueprint that usually mounts at "/"
    try:
        from app.main.routes import main_bp
        app.register_blueprint(main_bp)
    except Exception:
        # OK if you haven't created it yet
        pass

    # ---- Flask-Login: user loader ----
    from app.models import User
    @login_manager.user_loader
    def load_user(user_id: str):
        # Works on SQLAlchemy 2.x and avoids deprecated Query.get
        try:
            return db.session.get(User, int(user_id))
        except Exception:
            return None

    return app

# ... everything you already have in create_app() ...

    # ---- CLI commands (handy for servers) ----
    import click
    from app.models import User  # local import to avoid circulars

    @app.cli.command("create-admin")
    @click.argument("email")
    @click.argument("password")
    def create_admin(email, password):
        """Create an admin:  flask --app wsgi.py create-admin EMAIL PASSWORD"""
        # Works whether you're on SQLAlchemy 1.4 or 2.x
        exists = User.query.filter_by(email=email).first()
        if exists:
            click.echo("User already exists")
            return

        u = User(name="Admin", email=email, role="admin")
        u.set_password(password)           # uses your model's helper
        db.session.add(u)
        db.session.commit()
        click.echo(f"Admin created: {email}")

    return app


