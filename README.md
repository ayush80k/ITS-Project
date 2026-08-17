# Employee Management System (EMS)

A modular desktop-based Employee Management System built with Python, Tkinter, and SQLite.

## Default Demonstration Credentials

### Admin Portal Login:
* **Username:** `admin`
* **Password:** `admin123`

### Sample Employee Portal Logins:
* **Employee ID:** `EMP001` | **Password:** `emp123`
* **Employee ID:** `EMP002` | **Password:** `emp123`
* **Employee ID:** `EMP003` | **Password:** `emp123`

---

## Key Features

1. **Multi-Role Authentication:** Separate Admin and Employee portals with SHA-256 hashed password verification.
2. **Employee Management:** Complete CRUD interface, profile photo uploads, directory filtering, and admin password resets.
3. **Daily Batch Attendance:** Grid marking for Present/Absent/Leave per date and department with duplicate prevention.
4. **Attendance Reporting:** Monthly summaries, percentage calculations, and CSV export.
5. **Leave Management:** Inclusive date range calculation, employee submission portal, and admin approval/rejection workflows.
6. **Audit Trail:** Automatic logging of system activities and logins.
7. **Database Backup:** Snapshot database backup creation.

---

## Installation & Running

### Requirements
* Python 3.8+

### Setup Commands
```bash
# Clone or extract project directory
cd employee_management_system

# Run application
python main.py