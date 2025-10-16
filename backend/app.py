import os
import sys
from datetime import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.utils import secure_filename

print("🚀 Starting Event Management Backend...", file=sys.stderr)

# ---------------------------
# App Configuration
# ---------------------------
app = Flask(__name__)
CORS(app)

app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ---------------------------
# Database Setup
# ---------------------------
db = SQLAlchemy()

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "mysql+pymysql://event_user:event_password@localhost:3306/event_management"
)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_recycle": 300, "pool_pre_ping": True}

db.init_app(app)

with app.app_context():
    try:
        db.create_all()
        print("✅ Database connected and tables created successfully.", file=sys.stderr)
    except Exception as e:
        print(f"❌ Database initialization failed: {e}", file=sys.stderr)

# ---------------------------
# Models
# ---------------------------
class Event(db.Model):
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, default='')
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    tickets_sold = db.Column(db.Integer, default=0)

    attendees = db.relationship('Attendee', backref='event', cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'date': self.date.isoformat(),
            'location': self.location,
            'capacity': self.capacity,
            'tickets_sold': self.tickets_sold,
            'tickets_available': self.capacity - self.tickets_sold
        }

class Attendee(db.Model):
    __tablename__ = "attendees"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(50), default='')
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'registration_date': self.registration_date.isoformat(),
            'event_id': self.event_id,
            'event_title': self.event.title if self.event else None
        }

# ---------------------------
# CSV Import Check
# ---------------------------
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
    print("✅ Pandas available for CSV import", file=sys.stderr)
except ImportError:
    PANDAS_AVAILABLE = False
    print("⚠️ Pandas not available: CSV import will be limited", file=sys.stderr)

ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ---------------------------
# Health Check
# ---------------------------
@app.route('/health', methods=['GET'])
def health_check():
    try:
        Event.query.first()
        return jsonify({'status': 'healthy', 'database': 'connected', 'pandas_available': PANDAS_AVAILABLE})
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'database': 'disconnected', 'error': str(e)}), 500

# ---------------------------
# Event Routes
# ---------------------------
@app.route('/api/events', methods=['GET'])
def get_events():
    try:
        title = request.args.get('title', '')
        date = request.args.get('date', '')
        query = Event.query

        if title:
            query = query.filter(Event.title.ilike(f'%{title}%'))
        if date:
            try:
                dt = datetime.strptime(date, '%Y-%m-%d')
                query = query.filter(db.func.date(Event.date) == dt.date())
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

        events = query.order_by(Event.date.asc()).all()
        return jsonify([e.to_dict() for e in events])
    except Exception as e:
        app.logger.error(str(e))
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/events/<int:event_id>', methods=['GET'])
def get_event(event_id):
    event = Event.query.get_or_404(event_id)
    return jsonify(event.to_dict())

@app.route('/api/events', methods=['POST'])
def create_event():
    data = request.get_json()
    if not data: return jsonify({'error': 'No JSON data provided'}), 400

    required = ['title', 'date', 'location', 'capacity']
    for field in required:
        if field not in data or not data[field]:
            return jsonify({'error': f'{field} is required'}), 400

    try:
        event_date = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
        event = Event(
            title=data['title'],
            description=data.get('description', ''),
            date=event_date,
            location=data['location'],
            capacity=int(data['capacity'])
        )
        db.session.add(event)
        db.session.commit()
        return jsonify(event.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    event = Event.query.get_or_404(event_id)
    data = request.get_json()
    if not data: return jsonify({'error': 'No JSON data provided'}), 400

    try:
        if 'title' in data: event.title = data['title']
        if 'description' in data: event.description = data['description']
        if 'date' in data: event.date = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
        if 'location' in data: event.location = data['location']
        if 'capacity' in data:
            new_capacity = int(data['capacity'])
            if new_capacity < event.tickets_sold:
                return jsonify({'error': 'Capacity cannot be less than tickets sold'}), 400
            event.capacity = new_capacity

        db.session.commit()
        return jsonify(event.to_dict())
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    try:
        db.session.delete(event)
        db.session.commit()
        return jsonify({'message': 'Event deleted successfully'})
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

# ---------------------------
# Attendee Routes
# ---------------------------
@app.route('/api/attendees', methods=['POST'])
def create_attendee():
    data = request.get_json()
    if not data: return jsonify({'error': 'No JSON data provided'}), 400

    required = ['name', 'email', 'event_id']
    for field in required:
        if field not in data or not data[field]:
            return jsonify({'error': f'{field} is required'}), 400

    event = Event.query.get(data['event_id'])
    if not event: return jsonify({'error': 'Event not found'}), 404
    if event.tickets_sold >= event.capacity:
        return jsonify({'error': 'Event is full'}), 400

    existing = Attendee.query.filter_by(email=data['email'], event_id=data['event_id']).first()
    if existing: return jsonify({'error': 'Email already registered for this event'}), 400

    attendee = Attendee(
        name=data['name'],
        email=data['email'],
        phone=data.get('phone', ''),
        event_id=data['event_id']
    )
    event.tickets_sold += 1
    db.session.add(attendee)
    db.session.commit()
    return jsonify(attendee.to_dict()), 201

@app.route('/api/attendees/<int:attendee_id>', methods=['PUT'])
def update_attendee(attendee_id):
    attendee = Attendee.query.get_or_404(attendee_id)
    data = request.get_json()
    if not data: return jsonify({'error': 'No JSON data provided'}), 400

    if 'name' in data: attendee.name = data['name']
    if 'email' in data:
        if data['email'] != attendee.email:
            existing = Attendee.query.filter_by(email=data['email'], event_id=attendee.event_id).first()
            if existing: return jsonify({'error': 'Email already registered for this event'}), 400
        attendee.email = data['email']
    if 'phone' in data: attendee.phone = data['phone']

    db.session.commit()
    return jsonify(attendee.to_dict())

@app.route('/api/events/<int:event_id>/attendees', methods=['GET'])
def get_event_attendees(event_id):
    attendees = Attendee.query.filter_by(event_id=event_id).order_by(Attendee.registration_date.desc()).all()
    return jsonify([a.to_dict() for a in attendees])

# ---------------------------
# Reports Routes
# ---------------------------
@app.route('/api/reports/sales', methods=['GET'])
def get_sales_report():
    events = Event.query.all()
    report = {
        'total_events': len(events),
        'total_capacity': sum(e.capacity for e in events),
        'total_tickets_sold': sum(e.tickets_sold for e in events),
        'total_revenue': sum(e.tickets_sold * 100 for e in events),
        'events': []
    }
    for e in events:
        d = e.to_dict()
        d['revenue'] = e.tickets_sold * 100
        d['occupancy_rate'] = round((e.tickets_sold / e.capacity * 100), 2) if e.capacity else 0
        report['events'].append(d)
    return jsonify(report)

# ---------------------------
# CSV Import
# ---------------------------
@app.route('/api/events/import-csv', methods=['POST'])
def import_csv():
    if 'file' not in request.files: return jsonify({'error': 'No file provided'}), 400
    file = request.files['file']
    if not file.filename: return jsonify({'error': 'No file selected'}), 400
    if not allowed_file(file.filename): return jsonify({'error': 'Only CSV files allowed'}), 400
    if not PANDAS_AVAILABLE: return jsonify({'error': 'Pandas required for CSV import'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    df = pd.read_csv(filepath)
    required_cols = ['Event Title', 'Description', 'Date', 'Location', 'Capacity']
    for col in required_cols:
        if col not in df.columns:
            return jsonify({'error': f'Missing column: {col}'}), 400

    imported, errors = [], []
    for idx, row in df.iterrows():
        try:
            date = datetime.strptime(str(row['Date']), '%Y-%m-%d')
            e = Event(
                title=str(row['Event Title']),
                description=str(row['Description']),
                date=date,
                location=str(row['Location']),
                capacity=int(row['Capacity'])
            )
            db.session.add(e)
            db.session.flush()
            imported.append(e.to_dict())
        except Exception as ex:
            errors.append(f"Row {idx+1}: {ex}")
    if not imported:
        db.session.rollback()
        return jsonify({'error': 'All imports failed', 'details': errors}), 400
    db.session.commit()
    os.remove(filepath)
    response = {'message': f'Successfully imported {len(imported)} events', 'imported_events': imported}
    if errors: response['warnings'] = errors
    return jsonify(response), 201

# ---------------------------
# Start Server
# ---------------------------
if __name__ == '__main__':
    debug = os.environ.get('FLASK_ENV') == 'development'
    print("🎯 Starting Flask server...", file=sys.stderr)
    app.run(host='0.0.0.0', port=5000, debug=debug, use_reloader=debug)