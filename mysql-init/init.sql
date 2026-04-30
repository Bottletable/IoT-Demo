-- This file runs automatically when the MySQL container starts for the first time
USE flask_demo;

CREATE TABLE IF NOT EXISTS devices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    customer_name VARCHAR(255) NOT NULL,
    last_seen DATETIME NOT NULL,
    temperature FLOAT DEFAULT 0.0,
    vibration_level VARCHAR(50) DEFAULT 'normal',
    battery_health FLOAT DEFAULT 100.0,  -- INDSÆT DENNE
    yaw_error FLOAT DEFAULT 0.0,         -- INDSÆT DENNE
    error_code VARCHAR(50)               -- INDSÆT DENNE
);

INSERT INTO devices (name, location, status, customer_name, last_seen, temperature, vibration_level, battery_health, yaw_error, error_code)
VALUES 
('Sensor-ALB-001', 'Aalborg Wind Farm 1', 'online', 'Vestas', NOW(), 22.5, 'low', 100.0, 0.0, NULL),
('Sensor-ALB-002', 'Aalborg Wind Farm 1', 'maintenance', 'Vestas', NOW(), 55.2, 'heavy', 95.0, 5.0, 'ERR_VIB_01');