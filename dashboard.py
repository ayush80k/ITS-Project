import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import database
import utils

class DashboardView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill="both", expand=True)
        self.create_widgets()
        self.refresh_data()

    def create_widgets(self):
        header = ttk.Frame(self)
        header.pack(fill="x", padx=20, pady=(15, 10))
        
        ttk.Label(header, text="Admin Dashboard", font=("Segoe UI", 18, "bold"), foreground="#0f172a").pack(side="left")
        ttk.Button(header, text="Refresh Data", command=self.refresh_data, style="Secondary.TButton").pack(side="right")

        # Top Summary Cards
        cards_frame = ttk.Frame(self)
        cards_frame.pack(fill="x", padx=15, pady=5)

        self.card_total = self.create_card(cards_frame, "Total Employees", "0", 0, "#2563eb")
        self.card_active = self.create_card(cards_frame, "Active Staff", "0", 1, "#16a34a")
        self.card_on_leave = self.create_card(cards_frame, "Currently On Leave", "0", 2, "#d97706")
        self.card_depts = self.create_card(cards_frame, "Departments", "0", 3, "#6366f1")

        # Middle Panels: Attendance & Leave
        mid_frame = ttk.Frame(self)
        mid_frame.pack(fill="x", padx=15, pady=10)

        today_disp = utils.db_to_display_date(datetime.now().strftime('%Y-%m-%d'))
        att_group = ttk.LabelFrame(mid_frame, text=f"Today's Attendance Overview ({today_disp})")
        att_group.pack(side="left", fill="both", expand=True, padx=5)

        self.lbl_att_present = ttk.Label(att_group, text="● Present Today: 0", font=("Segoe UI", 10, "bold"), foreground="#16a34a")
        self.lbl_att_present.pack(anchor="w", padx=15, pady=6)

        self.lbl_att_absent = ttk.Label(att_group, text="● Absent Today: 0", font=("Segoe UI", 10, "bold"), foreground="#dc2626")
        self.lbl_att_absent.pack(anchor="w", padx=15, pady=6)

        self.lbl_att_leave = ttk.Label(att_group, text="● On Leave Today: 0", font=("Segoe UI", 10, "bold"), foreground="#d97706")
        self.lbl_att_leave.pack(anchor="w", padx=15, pady=6)

        self.lbl_att_unmarked = ttk.Label(att_group, text="● Not Marked Yet: 0", font=("Segoe UI", 10, "bold"), foreground="#64748b")
        self.lbl_att_unmarked.pack(anchor="w", padx=15, pady=6)

        leave_group = ttk.LabelFrame(mid_frame, text="Leave Requests Summary")
        leave_group.pack(side="right", fill="both", expand=True, padx=5)

        self.lbl_leave_pending = ttk.Label(leave_group, text="● Pending Requests: 0", font=("Segoe UI", 10, "bold"), foreground="#d97706")
        self.lbl_leave_pending.pack(anchor="w", padx=15, pady=6)

        self.lbl_leave_approved = ttk.Label(leave_group, text="● Approved Total: 0", font=("Segoe UI", 10, "bold"), foreground="#16a34a")
        self.lbl_leave_approved.pack(anchor="w", padx=15, pady=6)

        self.lbl_leave_rejected = ttk.Label(leave_group, text="● Rejected Total: 0", font=("Segoe UI", 10, "bold"), foreground="#dc2626")
        self.lbl_leave_rejected.pack(anchor="w", padx=15, pady=6)

        # Bottom Tables: Recent Staff & Activity Feed
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(fill="both", expand=True, padx=15, pady=(5, 15))

        emp_box = ttk.LabelFrame(bottom_frame, text="Recently Added Employees")
        emp_box.pack(side="left", fill="both", expand=True, padx=5)

        cols_emp = ("id", "name", "dept", "joining")
        self.table_recent_emp = ttk.Treeview(emp_box, columns=cols_emp, show="headings", height=5)
        self.table_recent_emp.heading("id", text="ID")
        self.table_recent_emp.heading("name", text="Name")
        self.table_recent_emp.heading("dept", text="Department")
        self.table_recent_emp.heading("joining", text="Joining Date")
        self.table_recent_emp.column("id", width=70)
        self.table_recent_emp.column("name", width=120)
        self.table_recent_emp.column("dept", width=110)
        self.table_recent_emp.column("joining", width=90)
        self.table_recent_emp.pack(fill="both", expand=True, padx=5, pady=5)

        act_box = ttk.LabelFrame(bottom_frame, text="Recent Activity Audit Trail")
        act_box.pack(side="right", fill="both", expand=True, padx=5)

        cols_act = ("time", "user", "action")
        self.table_recent_act = ttk.Treeview(act_box, columns=cols_act, show="headings", height=5)
        self.table_recent_act.heading("time", text="Timestamp")
        self.table_recent_act.heading("user", text="User")
        self.table_recent_act.heading("action", text="Action")
        self.table_recent_act.column("time", width=130)
        self.table_recent_act.column("user", width=80)
        self.table_recent_act.column("action", width=180)
        self.table_recent_act.pack(fill="both", expand=True, padx=5, pady=5)

    def create_card(self, parent, title, val, col, accent_color):
        frame = ttk.LabelFrame(parent, text=title)
        frame.grid(row=0, column=col, padx=5, pady=5, sticky="nsew")
        parent.columnconfigure(col, weight=1)

        lbl = ttk.Label(frame, text=val, font=("Segoe UI", 20, "bold"), foreground=accent_color)
        lbl.pack(padx=15, pady=10)
        return lbl

    def refresh_data(self):
        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            today_db = datetime.now().strftime("%Y-%m-%d")

            cursor.execute("SELECT COUNT(*) FROM employees")
            total_emps = cursor.fetchone()[0]
            self.card_total.config(text=str(total_emps))

            cursor.execute("SELECT COUNT(*) FROM employees WHERE status='Active'")
            active_emps = cursor.fetchone()[0]
            self.card_active.config(text=str(active_emps))

            cursor.execute("""
            SELECT COUNT(DISTINCT employee_id) FROM leaves 
            WHERE status='Approved' AND ? BETWEEN start_date AND end_date
            """, (today_db,))
            currently_on_leave = cursor.fetchone()[0]
            self.card_on_leave.config(text=str(currently_on_leave))

            cursor.execute("SELECT COUNT(DISTINCT department) FROM employees")
            depts = cursor.fetchone()[0]
            self.card_depts.config(text=str(depts))

            cursor.execute("SELECT status, COUNT(*) FROM attendance WHERE date=? GROUP BY status", (today_db,))
            att_counts = dict(cursor.fetchall())
            pres = att_counts.get("Present", 0)
            absn = att_counts.get("Absent", 0)
            leav = att_counts.get("Leave", 0)

            cursor.execute("SELECT COUNT(DISTINCT employee_id) FROM attendance WHERE date=?", (today_db,))
            marked_total = cursor.fetchone()[0]
            unmarked = max(0, active_emps - marked_total)

            self.lbl_att_present.config(text=f"● Present Today: {pres}")
            self.lbl_att_absent.config(text=f"● Absent Today: {absn}")
            self.lbl_att_leave.config(text=f"● On Leave Today: {leav}")
            self.lbl_att_unmarked.config(text=f"● Not Marked Yet: {unmarked}")

            cursor.execute("SELECT status, COUNT(*) FROM leaves GROUP BY status")
            leave_counts = dict(cursor.fetchall())
            self.lbl_leave_pending.config(text=f"● Pending Requests: {leave_counts.get('Pending', 0)}")
            self.lbl_leave_approved.config(text=f"● Approved Total: {leave_counts.get('Approved', 0)}")
            self.lbl_leave_rejected.config(text=f"● Rejected Total: {leave_counts.get('Rejected', 0)}")

            for item in self.table_recent_emp.get_children():
                self.table_recent_emp.delete(item)
            cursor.execute("SELECT employee_id, name, department, joining_date FROM employees ORDER BY rowid DESC LIMIT 5")
            for row in cursor.fetchall():
                display_row = (row[0], row[1], row[2], utils.db_to_display_date(row[3]))
                self.table_recent_emp.insert("", "end", values=display_row)

            for item in self.table_recent_act.get_children():
                self.table_recent_act.delete(item)
            cursor.execute("SELECT timestamp, user_id, action FROM activity_log ORDER BY activity_id DESC LIMIT 5")
            for row in cursor.fetchall():
                self.table_recent_act.insert("", "end", values=row)

            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh dashboard: {e}")
