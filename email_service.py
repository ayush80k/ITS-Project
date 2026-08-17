import smtplib
from email.mime.text import MIMEText
import database

def get_email_config():
    try:
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT setting_key, setting_value FROM app_settings WHERE setting_key LIKE 'email_%'")
        rows = dict(cursor.fetchall())
        conn.close()
        
        if rows.get("email_enabled") == "True":
            return {
                "server": rows.get("email_server", "smtp.gmail.com"),
                "port": int(rows.get("email_port", 587)),
                "sender": rows.get("email_sender", ""),
                "password": rows.get("email_password", "")
            }
    except Exception:
        pass
    return None

def send_email_notification(recipient_email, subject, body):
    config = get_email_config()
    if not config or not config["sender"] or not config["password"]:
        print(f"[Email Service Disabled] Simulated email to '{recipient_email}': Subject: {subject}")
        return False, "Email notifications are disabled or not configured."

    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = config["sender"]
        msg['To'] = recipient_email

        with smtplib.SMTP(config["server"], config["port"], timeout=5) as server:
            server.starttls()
            server.login(config["sender"], config["password"])
            server.send_message(msg)
        return True, "Email sent successfully."
    except Exception as e:
        return False, f"Failed to send email: {e}"
