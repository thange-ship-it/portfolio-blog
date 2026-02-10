"""Seed the database with a default admin user."""
import os
from dotenv import load_dotenv

load_dotenv()

from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    # Create admin user if not exists
    username = os.environ.get('ADMIN_USERNAME', 'admin')
    password = os.environ.get('ADMIN_PASSWORD', 'changeme123')

    existing = User.query.filter_by(username=username).first()
    if not existing:
        admin = User(username=username)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        print(f"Admin user '{username}' created.")
    else:
        print(f"Admin user '{username}' already exists.")
