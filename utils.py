import os
import sys
import re
import hashlib
from datetime import datetime

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def hash_password(password):
    if not password:
        return ""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(stored_hash, input_password):
    return stored_hash == hash_password(input_password)

def display_to_db_date(date_str):
    if not date_str:
        return ""
    try:
        dt = datetime.strptime(date_str.strip(), "%d-%m-%Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        try:
            dt = datetime.strptime(date_str.strip(), "%Y-%m-%d")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            return None

def db_to_display_date(date_str):
    if not date_str:
        return ""
    try:
        dt = datetime.strptime(date_str.strip(), "%Y-%m-%d")
        return dt.strftime("%d-%m-%Y")
    except ValueError:
        return date_str

def validate_date(date_str):
    return display_to_db_date(date_str) is not None

def calculate_inclusive_days(start_str, end_str):
    db_start = display_to_db_date(start_str)
    db_end = display_to_db_date(end_str)
    if not db_start or not db_end:
        return 0
    d1 = datetime.strptime(db_start, "%Y-%m-%d")
    d2 = datetime.strptime(db_end, "%Y-%m-%d")
    if d2 < d1:
        return -1
    return (d2 - d1).days + 1

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))

def validate_phone(phone):
    cleaned = phone.strip()
    return cleaned.isdigit() and len(cleaned) == 10

def validate_number(val):
    try:
        float(val)
        return True
    except (ValueError, TypeError):
        return False
