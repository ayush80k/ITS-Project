import tkinter as tk
from tkinter import ttk, messagebox
import database
import utils
from activity_logger import log_activity
from email_service import send_email_notification

class LeaveView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill="both", expand=True)

        self.selected_leave_id = None
        self.create_widgets()
        self.load_leaves()

    def create_widgets(self):
        top_frame = ttk.Frame(self)
        top_frame.pack(fill="x", padx=15, pady=(15, 10))

        ttk.Label(top_frame, text="Leave Requests Review", font=("Segoe UI", 16, "bold"), foreground="#0f172a").pack(side="left")

        ttk.Label(top_frame, text="Filter Status:").pack(side="left", padx=(30, 5))
        self.combo_status_filter = ttk.Combobox(top_frame, values=["All", "Pending", "Approved", "Rejected"], state="readonly", width=12)
        self.combo_status_filter.set("Pending")
        self.combo_status_filter.pack(side="left", padx=5)
        ttk.Button(top_frame, text="Apply Filter", command=self.load_leaves, style="Secondary.TButton").pack(side="left", padx=5)

        table_frame = ttk.LabelFrame(self, text="Applications List")
        table_frame.pack(fill="both", expand=True, padx=15, pady=5)

        columns = ("id", "emp_id", "emp_name", "type", "start", "end", "days", "reason", "status")
        self.table = ttk.Treeview(table_frame, columns=columns, show="headings")

        self.table.heading("id", text="Leave ID")
        self.table.heading("emp_id", text="Emp ID")
        self.table.heading("emp_name", text="Name")
        self.table.heading("type", text="Type")
        self.table.heading("start", text="Start Date")
        self.table.heading("end", text="End Date")
        self.table.heading("days", text="Days")
        self.table.heading("reason", text="Reason")
        self.table.heading("status", text="Status")

        self.table.column("id", width=60)
        self.table.column("emp_id", width=80)
        self.table.column("emp_name", width=120)
        self.table.column("type", width=90)
        self.table.column("start", width=90)
        self.table.column("end", width=90)
        self.table.column("days", width=50)
        self.table.column("reason", width=200)
        self.table.column("status", width=100)

        self.table.tag_configure("Pending", foreground="#d97706")
        self.table.tag_configure("Approved", foreground="#16a34a")
        self.table.tag_configure("Rejected", foreground="#dc2626")

        self.table.pack(fill="both", expand=True, padx=5, pady=5)
        self.table.bind("<<TreeviewSelect>>", self.on_select_row)

        action_bar = ttk.Frame(self)
        action_bar.pack(fill="x", padx=15, pady=10)

        ttk.Button(action_bar, text="Approve Request", command=lambda: self.update_status("Approved"), style="Success.TButton").pack(side="left", padx=5)
        ttk.Button(action_bar, text="Reject Request", command=lambda: self.update_status("Rejected"), style="Destructive.TButton").pack(side="left", padx=5)

    def on_select_row(self, event):
        selected_item = self.table.selection()
        if selected_item:
            values = self.table.item(selected_item[0])['values']
            if values and str(values[0]) != "No records found":
                self.selected_leave_id = values[0]

    def update_status(self, new_status):
        if not self.selected_leave_id:
            messagebox.showwarning("Selection Required", "Please select a leave request from the table.")
            return

        confirm = messagebox.askyesno("Confirm Action", f"Are you sure you want to mark this request as '{new_status}'?")
        if not confirm:
            return

        try:
            conn = database.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
            SELECT l.employee_id, e.name, e.email, l.leave_type 
            FROM leaves l JOIN employees e ON l.employee_id = e.employee_id 
            WHERE l.leave_id=?
            """, (self.selected_leave_id,))
            row = cursor.fetchone()

            cursor.execute("UPDATE leaves SET status=? WHERE leave_id=?", (new_status, self.selected_leave_id))
            conn.commit()
            conn.close()

            if row:
                emp_id, emp_name, emp_email, leave_type = row
                log_activity("ADMIN", "Admin", f"Leave {new_status}", f"{new_status} {leave_type} leave request for {emp_name} ({emp_id})")
                send_email_notification(emp_email, f"Leave Request {new_status}", f"Hello {emp_name},\n\nYour {leave_type} leave request has been {new_status.lower()}.\n\nEMS Admin")

            messagebox.showinfo("Success", f"Leave application marked as '{new_status}'.")
            self.selected_leave_id = None
            self.load_leaves()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update leave status: {e}")

    def load_leaves(self):
        for item in self.table.get_children():
            self.table.delete(item)

        filter_status = self.combo_status_filter.get()

        conn = database.get_connection()
        cursor = conn.cursor()

        query = """
        SELECT l.leave_id, l.employee_id, e.name, l.leave_type, l.start_date, l.end_date, l.reason, l.status
        FROM leaves l JOIN employees e ON l.employee_id = e.employee_id
        """
        params = []
        if filter_status != "All":
            query += " WHERE l.status=?"
            params.append(filter_status)

        query += " ORDER BY l.leave_id DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            self.table.insert("", "end", values=("No records found", "", "", "", "", "", "", "", ""))
            return

        for row in rows:
            start_disp = utils.db_to_display_date(row[4])
            end_disp = utils.db_to_display_date(row[5])
            days = utils.calculate_inclusive_days(start_disp, end_disp)
            display_row = (row[0], row[1], row[2], row[3], start_disp, end_disp, days, row[6], f"● {row[7]}")
            self.table.insert("", "end", values=display_row, tags=(row[7],))
