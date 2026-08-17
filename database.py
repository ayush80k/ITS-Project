import sqlite3
import os
import shutil
from datetime import datetime
from utils import hash_password, resource_path

DB_NAME = "employee_management.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        employee_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        gender TEXT NOT NULL,
        dob TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        address TEXT NOT NULL,
        department TEXT NOT NULL,
        designation TEXT NOT NULL,
        joining_date TEXT NOT NULL,
        employment_type TEXT NOT NULL,
        salary REAL NOT NULL,
        status TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        photo_path TEXT DEFAULT ''
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id TEXT NOT NULL,
        date TEXT NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (employee_id) REFERENCES employees (employee_id) ON DELETE CASCADE,
        UNIQUE(employee_id, date)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leaves (
        leave_id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id TEXT NOT NULL,
        leave_type TEXT NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        reason TEXT NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (employee_id) REFERENCES employees (employee_id) ON DELETE CASCADE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS activity_log (
        activity_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        role TEXT NOT NULL,
        action TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        description TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS app_settings (
        setting_key TEXT PRIMARY KEY,
        setting_value TEXT NOT NULL
    )
    """)

    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM users WHERE username='admin'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users VALUES (?, ?, ?)", ("admin", hash_password("admin123"), "Admin"))
        conn.commit()

    cursor.execute("SELECT COUNT(*) FROM employees")
    if cursor.fetchone()[0] == 0:
        seed_sample_data(cursor)
        conn.commit()

    conn.close()

    os.makedirs(resource_path("assets/employee_photos"), exist_ok=True)
    os.makedirs(resource_path("backups"), exist_ok=True)

def seed_sample_data(cursor):
    sample_emps = [
        ("EMP001", "Aarav Sharma", "Male", "1995-05-15", "aarav.sharma@example.com", "9876543210", "12 Park Street, Jaipur", "Software Development", "Senior Developer", "2022-01-10", "Full-Time", 85000.0, "Active", hash_password("emp123"), ""),
        ("EMP002", "Priya Verma", "Female", "1998-08-22", "priya.verma@example.com", "9876543211", "45 MI Road, Jaipur", "Human Resources", "HR Executive", "2023-03-15", "Full-Time", 52000.0, "Active", hash_password("emp123"), ""),
        ("EMP003", "Rohan Mehta", "Male", "1996-11-02", "rohan.mehta@example.com", "9876543212", "78 Tonk Road, Jaipur", "Marketing", "Marketing Lead", "2021-07-01", "Full-Time", 68000.0, "Active", hash_password("emp123"), ""),
        ("EMP004", "Ananya Sen", "Female", "1999-02-18", "ananya.sen@example.com", "9876543213", "101 Vaishali Nagar, Jaipur", "Finance", "Accountant", "2023-09-01", "Full-Time", 48000.0, "Active", hash_password("emp123"), ""),
        ("EMP005", "Kabir Nair", "Male", "1994-12-30", "kabir.nair@example.com", "9876543214", "22 Raja Park, Jaipur", "Software Development", "QA Lead", "2020-05-12", "Full-Time", 75000.0, "Active", hash_password("emp123"), ""),
        ("EMP006", "Sneha Joshi", "Female", "1997-04-10", "sneha.joshi@example.com", "9876543215", "56 Mansarovar, Jaipur", "Sales", "Sales Executive", "2022-11-20", "Full-Time", 45000.0, "Active", hash_password("emp123"), ""),
        ("EMP007", "Vikram Rathore", "Male", "1993-09-05", "vikram.rathore@example.com", "9876543216", "89 C-Scheme, Jaipur", "Administration", "Admin Manager", "2019-02-01", "Full-Time", 60000.0, "Active", hash_password("emp123"), ""),
        ("EMP008", "Neha Gupta", "Female", "2000-01-25", "neha.gupta@example.com", "9876543217", "14 Malviya Nagar, Jaipur", "Software Development", "Junior Developer", "2024-01-15", "Full-Time", 40000.0, "Active", hash_password("emp123"), "")
    ]
    cursor.executemany("INSERT INTO employees VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", sample_emps)

    sample_att = [
        ("EMP001", "2026-08-12", "Present"),
        ("EMP002", "2026-08-12", "Present"),
        ("EMP003", "2026-08-12", "Leave"),
        ("EMP004", "2026-08-12", "Present"),
        ("EMP005", "2026-08-12", "Absent"),
        ("EMP006", "2026-08-12", "Present"),
        ("EMP007", "2026-08-12", "Present"),
        ("EMP008", "2026-08-12", "Present")
    ]
    cursor.executemany("INSERT INTO attendance (employee_id, date, status) VALUES (?,?,?)", sample_att)

    sample_leaves = [
        ("EMP003", "Casual", "2026-08-12", "2026-08-14", "Family Function", "Approved"),
        ("EMP005", "Medical", "2026-08-12", "2026-08-12", "Fever", "Rejected"),
        ("EMP008", "Casual", "2026-08-15", "2026-08-16", "Personal Work", "Pending")
    ]
    cursor.executemany("INSERT INTO leaves (employee_id, leave_type, start_date, end_date, reason, status) VALUES (?,?,?,?,?,?)", sample_leaves)

    cursor.execute("INSERT INTO activity_log (user_id, role, action, timestamp, description) VALUES (?,?,?,?,?)",
                   ("SYSTEM", "System", "Database Initialization", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Sample database created and seeded successfully."))

def backup_database(dest_folder=None):
    if not dest_folder:
        dest_folder = resource_path("backups")
    os.makedirs(dest_folder, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_filename = f"employee_management_{timestamp}.db"
    dest_path = os.path.join(dest_folder, backup_filename)
    shutil.copy2(DB_NAME, dest_path)
    return dest_path
