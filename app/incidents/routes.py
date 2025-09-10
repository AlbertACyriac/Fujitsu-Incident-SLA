from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import db
from app.models import Incident, Client, SLA
from app.utils import admin_required

incidents_bp = Blueprint("incidents", __name__, template_folder="../templates")


# ----- helpers ---------------------------------------------------------------

def _to_int(v, default=0):
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def _user_can_edit(incident: Incident) -> bool:
    """Admins can edit everything; regular users only their own incidents."""
    return current_user.is_admin or incident.created_by == current_user.id


# ----- routes ----------------------------------------------------------------

@incidents_bp.route("/", methods=["GET"])
@login_required
def index():
    """List incidents (all for admins, own for regular users)."""
    if current_user.is_admin:
        incidents = Incident.query.order_by(Incident.created_at.desc()).all()
    else:
        incidents = (
            Incident.query.filter_by(created_by=current_user.id)
            .order_by(Incident.created_at.desc())
            .all()
        )

    clients = Client.query.order_by(Client.name).all()
    slas = SLA.query.order_by(SLA.name).all()
    return render_template(
        "incidents/list.html",
        incidents=incidents,
        clients=clients,
        slas=slas,
    )


@incidents_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    """Create a new incident."""
    clients = Client.query.order_by(Client.name).all()
    slas = SLA.query.order_by(SLA.name).all()

    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        description = (request.form.get("description") or "").strip()
        priority = (request.form.get("priority") or "Low").strip()
        status = (request.form.get("status") or "Open").strip()
        client_id = _to_int(request.form.get("client_id"))
        sla_id = _to_int(request.form.get("sla_id"))

        # minimal validation
        if not title or not client_id or not sla_id:
            flash("Title, Client and SLA are required.", "danger")
            return render_template(
                "incidents/form.html",
                incident=None,
                clients=clients,
                slas=slas,
            )

        inc = Incident(
            title=title,
            description=description,
            priority=priority,
            status=status,
            client_id=client_id,
            sla_id=sla_id,
            created_by=current_user.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.session.add(inc)
        db.session.commit()
        flash("Incident created.", "success")
        return redirect(url_for("incidents.index"))

    return render_template("incidents/form.html", incident=None, clients=clients, slas=slas)


@incidents_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit(id):
    """Edit an existing incident (respect ownership for regular users)."""
    inc = Incident.query.get_or_404(id)
    if not _user_can_edit(inc):
        abort(403)

    clients = Client.query.order_by(Client.name).all()
    slas = SLA.query.order_by(SLA.name).all()

    if request.method == "POST":
        inc.title = (request.form.get("title") or "").strip()
        inc.description = (request.form.get("description") or "").strip()
        inc.priority = (request.form.get("priority") or "Low").strip()
        inc.status = (request.form.get("status") or "Open").strip()
        inc.client_id = _to_int(request.form.get("client_id"))
        inc.sla_id = _to_int(request.form.get("sla_id"))
        inc.updated_at = datetime.utcnow()

        if not inc.title or not inc.client_id or not inc.sla_id:
            flash("Title, Client and SLA are required.", "danger")
            return render_template(
                "incidents/form.html",
                incident=inc,
                clients=clients,
                slas=slas,
            )

        db.session.commit()
        flash("Incident updated.", "success")
        return redirect(url_for("incidents.index"))

    return render_template("incidents/form.html", incident=inc, clients=clients, slas=slas)


@incidents_bp.route("/<int:id>/delete", methods=["POST"])
@login_required
@admin_required
def delete(id):
    """Delete an incident (admin only)."""
    inc = Incident.query.get_or_404(id)
    db.session.delete(inc)
    db.session.commit()
    flash("Incident deleted.", "warning")
    return redirect(url_for("incidents.index"))

