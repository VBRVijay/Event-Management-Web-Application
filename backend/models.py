from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    tickets_sold = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    attendees = db.relationship('Attendee', backref='event', lazy=True, cascade='all, delete-orphan')

    @property
    def tickets_available(self):
    return self.capacity - self.tickets_sold

    def __repr__(self):
    return f'<Event {self.title}>'

class Attendee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
    return f'<Attendee {self.name}>'