-- Create database (if not already created by environment variables)
CREATE DATABASE IF NOT EXISTS event_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Use the database
USE event_management;


-- Create user and grant privileges (this is what you currently have)
CREATE USER IF NOT EXISTS 'eventuser'@'%' IDENTIFIED BY 'eventpass123';
GRANT ALL PRIVILEGES ON event_management.* TO 'eventuser'@'%';
FLUSH PRIVILEGES;

-- ========== THIS IS WHAT'S MISSING ==========

-- Create events table
CREATE TABLE IF NOT EXISTS events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    date DATETIME NOT NULL,
    location VARCHAR(200) NOT NULL,
    capacity INT NOT NULL,

    tickets_sold INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_date (date),
    INDEX idx_location (location)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create attendees table
CREATE TABLE IF NOT EXISTS attendees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL,
    phone VARCHAR(20),
    event_id INT NOT NULL,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    UNIQUE KEY unique_email_event (email, event_id),
    INDEX idx_event_id (event_id),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert sample events
INSERT IGNORE INTO events (id, title, description, date, location, capacity, tickets_sold) VALUES
(1, 'Tech Conference 2024', 'Annual technology conference featuring latest innovations in AI, Web Development, and Cloud Computing', '2024-06-15 09:00:00', 'Convention Center, Bangalore', 500, 125),
(2, 'Music Festival', 'Weekend music festival with various artists and food 

stalls', '2024-07-20 14:00:00', 'Central Park, Mumbai', 1000, 750),
(3, 'Business Workshop', 'Entrepreneurship and business development workshop for startups', '2024-05-10 10:00:00', 'Business Hub, Delhi', 100, 45),
(4, 'Charity Gala Dinner', 'Annual charity event to raise funds for education', '2024-08-05 19:00:00', 'Grand Hotel, Chennai', 200, 120),
(5, 'Sports Tournament', 'Inter-company sports competition with multiple games', '2024-09-12 08:00:00', 'Sports Complex, Hyderabad', 300, 180);

-- Insert sample attendees
INSERT IGNORE INTO attendees (name, email, phone, event_id) VALUES
('Rajesh Kumar', 'rajesh.kumar@email.com', '+91-9876543210', 1),

('Priya Sharma', 'priya.sharma@email.com', '+91-9876543211', 1),
('Amit Patel', 'amit.patel@email.com', '+91-9876543212', 1),
('Sneha Reddy', 'sneha.reddy@email.com', '+91-9876543213', 2),
('Vikram Singh', 'vikram.singh@email.com', '+91-9876543214', 2),
('Anjali Mehta', 'anjali.mehta@email.com', '+91-9876543215', 3),
('Rahul Verma', 'rahul.verma@email.com', '+91-9876543216', 3),
('Pooja Joshi', 'pooja.joshi@email.com', '+91-9876543217', 4),
('Karthik Nair', 'karthik.nair@email.com', '+91-9876543218', 4),
('Divya Gupta', 'divya.gupta@email.com', '+91-9876543219', 5);

-- Verification queries (optional)
SELECT 'Database initialized successfully!' 

as status;
SELECT COUNT(*) as event_count FROM events;
SELECT COUNT(*) as attendee_count FROM attendees;
