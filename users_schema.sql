-- Analytical Platform Pro: Database Schema Template

-- Users table for authentication
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    is_admin INTEGER DEFAULT 0
);

-- User-specific dashboard widgets
CREATE TABLE IF NOT EXISTS user_widgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    dataset_key TEXT NOT NULL,
    chart_type TEXT NOT NULL,
    x_axis TEXT NOT NULL,
    y_axis TEXT,
    FOREIGN KEY(username) REFERENCES users(username)
);

-- Optional: Initial Admin User
-- Note: Password 'admin123' hashed with bcrypt would go in password_hash
-- It is recommended to use the provided init_database.py script to handle hashing correctly.
