from datetime import datetime
import database

def log_activity(user_id, role, action, description):
    try:
        conn = database.get_connection()
        cursor = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
        INSERT INTO activity_log (user_id, role, action, timestamp, description)
        VALUES (?, ?, ?, ?, ?)
        """, (str(user_id), str(role), str(action), timestamp, str(description)))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[ActivityLogger Error]: {e}")
