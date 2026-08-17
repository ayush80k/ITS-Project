import tkinter as tk
from tkinter import ttk, messagebox
import database

class ActivityLogView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill="both", expand=True)
        self.create_widgets()
        self.load_logs()

    def create_widgets(self):
        header = ttk.Frame(self)
        header.pack(fill="x", padx=15, pady=(15, 10))
        ttk.Label(header, text="System Activity & Audit Logs", font=("Segoe UI", 16, "bold"), foreground="#0f172a").pack(side="left")
        ttk.Button(header, text="Refresh Logs", command=self.load_logs, style="Secondary.TButton").pack(side="right")

        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=15, pady=5)

        columns = ("id", "timestamp", "user", "role", "action", "desc")
        self.table = ttk.Treeview(table_frame, columns=columns, show="headings")

        self.table.heading("id", text="Log ID")
        self.table.heading("timestamp", text="Timestamp")
        self.table.heading("user", text="User / Emp ID")
        self.table.heading("role", text="Role")
        self.table.heading("action", text="Action")
        self.table.heading("desc", text="Description")

        self.table.column("id", width=60)
        self.table.column("timestamp", width=140)
        self.table.column("user", width=90)
        self.table.column("role", width=80)
        self.table.column("action", width=140)
        self.table.column("desc", width=350)

        self.table.pack(fill="both", expand=True)

    def load_logs(self):
        for item in self.table.get_children():
            self.table.delete(item)

        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT activity_id, timestamp, user_id, role, action, description FROM activity_log ORDER BY activity_id DESC")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            self.table.insert("", "end", values=("No records found", "", "", "", "", ""))
            return

        for row in rows:
            self.table.insert("", "end", values=row)
