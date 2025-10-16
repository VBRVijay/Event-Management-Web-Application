"""
database.py
--------------------------------------
Handles database configuration and initialization
for the Event Management Flask web application.
--------------------------------------
"""

from flask_sqlalchemy import SQLAlchemy
import os
import pymysql

# Initialize SQLAlchemy instance
db = SQLAlchemy()

def init_db(app):
    """
    Initialize the database connection for the Flask app.
    Reads DATABASE_URL from environment variables (used in Docker),
    or falls back to a local default MySQL connection.
    """

    # Default connection (local development)
    default_db_url = "mysql+pymysql://event_user:event_password@localhost:3306/event_management"

    # Use DATABASE_URL from environment variable if provided
    database_url = os.environ.get("DATABASE_URL", default_db_url)

    # Configure SQLAlchemy connection settings
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,   # refresh connections every 5 minutes
        "pool_pre_ping": True  # automatically check connections
    }

    # Bind the app with the SQLAlchemy instance
    db.init_app(app)

    # Create database tables automatically
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database connected and tables created successfully.")
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
