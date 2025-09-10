from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models import SLA
from app.utils import admin_required

slas_bp = Blueprint("slas", __name__)

@slas_bp.route("/")
@login_required
def index():
    slas = SLA.query.order_by(SLA.name).all()
    return render_template("slas/list.html", slas=slas)

@slas_bp.route("/create", methods=["GET", "POST"])
@login_required
@admin_required
def create():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        resp = int(request.form.get("target_response_mins") or 0)
        reso = int(request.form.get("target_resolve_mins") or 0)
        if not name:
            flash("Name is required.", "danger")
            return render_template("slas/form.html")
        db.session.add(SLA(name=name, target_response_mins=resp, target_resolve_mins=reso))
        db.session.commit()
        flash("SLA created.", "success")
        return redirect(url_for("slas.index"))
    return render_template("slas/form.html")

@slas_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit(id):
    sla = SLA.query.get_or_404(id)
    if request.method == "POST":
        sla.name = request.form.get("name", "").strip()
        sla.target_response_mins = int(request.form.get("target_response_mins") or 0)
        sla.target_resolve_mins = int(request.form.get("target_resolve_mins") or 0)
        db.session.commit()
        flash("SLA updated.", "success")
        return redirect(url_for("slas.index"))
    return render_template("slas/form.html", sla=sla)

@slas_bp.route("/<int:id>/delete", methods=["POST"])
@login_required
@admin_required
def delete(id):
    sla = SLA.query.get_or_404(id)
    db.session.delete(sla)
    db.session.commit()
    flash("SLA deleted.", "warning")
    return redirect(url_for("slas.index"))

