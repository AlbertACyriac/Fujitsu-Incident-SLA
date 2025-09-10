# seed.py
"""
Seed the Fujitsu Incident & SLA Tracker database with demo data.

- Clears and recreates the schema (safe for local dev).
- Ensures at least 10 Users, 10 Clients, 10 SLAs.
- Creates 30 Incidents linked to those rows.
"""

from random import choice, randint
from datetime import datetime, timedelta, timezone

from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models import User, Client, SLA, Incident


# ---------- config ----------
RESET_SCHEMA = True          # drop_all/create_all before seeding
NUM_USERS    = 10            # includes 1 admin + 9 regular
NUM_CLIENTS  = 10
NUM_SLAS     = 10
NUM_INCIDENTS = 30
# ----------------------------

app = create_app()

def now_utc():
    return datetime.now(tz=timezone.utc)

def seed_users():
    """Create 1 admin + (NUM_USERS-1) regular users."""
    users = []

    # Admin
    users.append(
        User(
            name="Service Manager",
            email="admin@fujitsu.com",
            password_hash=generate_password_hash("Admin123!"),
            role="admin",
        )
    )

    # Regulars
    for i in range(1, NUM_USERS):
        users.append(
            User(
                name=f"Analyst {i}",
                email=f"analyst{i}@fujitsu.com",
                password_hash=generate_password_hash("Analyst123!"),
                role="regular",
            )
        )

    db.session.add_all(users)
    db.session.flush()  # to allocate IDs
    return users


def seed_clients():
    sectors = ["Finance", "Retail", "Public", "Manufacturing", "Energy"]
    clients = [
        Client(
            name=f"Client {i}",
            sector=choice(sectors),
            contact_email=f"client{i}@example.com",
        )
        for i in range(1, NUM_CLIENTS + 1)
    ]
    db.session.add_all(clients)
    db.session.flush()
    return clients


def seed_slas():
    # 10 sensible SLA tiers
    tiers = [
        ("Basic",      300, 1440),
        ("Standard",   240, 1440),
        ("Standard+",  180,  720),
        ("Gold",       120,  480),
        ("Premium",     90,  360),
        ("Express",     60,  240),
        ("Platinum",    30,  120),
        ("Critical",    15,   60),
        ("Enterprise",  45,  180),
        ("Bronze",     360, 2160),
    ]
    slas = [SLA(name=n, target_response_mins=resp, target_resolve_mins=reso) for n, resp, reso in tiers[:NUM_SLAS]]
    db.session.add_all(slas)
    db.session.flush()
    return slas


def seed_incidents(users, clients, slas):
    statuses  = ["Open", "In-Progress", "Resolved", "Closed"]
    priorities = ["Low", "Medium", "High"]

    # pick only regular users as creators (admin supervises)
    regular_users = [u for u in users if u.role != "admin"] or users

    for i in range(1, NUM_INCIDENTS + 1):
        created = now_utc() - timedelta(days=randint(0, 30))
        inc = Incident(
            title=f"Service disruption #{i}",
            description=f"Auto-seeded incident #{i}: simulated ticket for demo data.",
            priority=choice(priorities),
            status=choice(statuses),
            client_id=choice(clients).id,
            sla_id=choice(slas).id,
            created_by=choice(regular_users).id,
            created_at=created,
            updated_at=created + timedelta(hours=randint(0, 72)),
        )
        db.session.add(inc)


if __name__ == "__main__":
    with app.app_context():
        if RESET_SCHEMA:
            db.drop_all()
            db.create_all()

        users   = seed_users()
        clients = seed_clients()
        slas    = seed_slas()

        seed_incidents(users, clients, slas)
        db.session.commit()

        print("✅ Seed complete!")
        print(f"Users:     {User.query.count()}")
        print(f"Clients:   {Client.query.count()}")
        print(f"SLAs:      {SLA.query.count()}")
        print(f"Incidents: {Incident.query.count()}")

