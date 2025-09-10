# app/auth/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User

# Point to the shared templates dir
auth_bp = Blueprint("auth", __name__, template_folder="../../templates")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    # Already logged-in users shouldn't register again
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        # Basic validation
        if not name or not email or not password:
            flash("All fields are required.", "error")
            return render_template("auth/register.html")

        # Unique email
        if User.query.filter_by(email=email).first():
            flash("Email is already registered.", "error")
            return render_template("auth/register.html")

        # Create regular user; promote via DB later if you need an admin
        user = User(name=name, email=email, role="regular")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Account created. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash("Invalid email or password.", "error")
            return render_template("auth/login.html")

        login_user(user)
        flash(f"Welcome back, {user.name}", "success")

        # Support ?next=/some/path redirect after login
        next_url = request.args.get("next") or url_for("main.index")
        return redirect(next_url)

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    name = current_user.name
    logout_user()
    flash(f"Logged out {name}.", "success")
    return redirect(url_for("auth.login"))

