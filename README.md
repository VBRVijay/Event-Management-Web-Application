# Event Management System

A full-stack web application for managing events, attendees, and generating sales reports. Built with Flask backend, vanilla JavaScript frontend, MySQL database, and containerized with Docker.

## 🚀 Features

### Event Management
- Create, read, update, and delete events
- Search events by title and date
- Event capacity management
- Real-time ticket availability tracking

### Attendee Management
- Register attendees for events
- Edit attendee information
- Prevent duplicate registrations
- Capacity validation

### Sales Reports
- Comprehensive sales dashboard
- Revenue tracking ($100 per ticket)
- Occupancy rate calculations
- Export reports to CSV

### Data Import
- Bulk import events from CSV files
- Drag & drop file upload
- Validation and error handling

## 🛠️ Technology Stack

**Backend:**
- Flask 2.3.3
- SQLAlchemy ORM
- PyMySQL
- Gunicorn WSGI server
- Pandas (for CSV processing)

**Frontend:**
- JavaScript
- HTML5 & CSS3
- Responsive design

**Database:**
- MySQL 8.0

**Infrastructure:**
- Docker & Docker Compose

## 🚀 Quick Start

1. **Clone and run the application**
   ```bash
   docker-compose up -d