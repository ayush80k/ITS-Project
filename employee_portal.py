import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import database
import utils
from activity_logger import log_activity

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

class EmployeePortalView(ttk.Frame):
    def __init__(self, parent, employee_id, logout_callback):
        super().__init__(parent)
        self.pack(fill="both", expand=True)
        self.employee_id = employee_id
        self.logout_callback = logout_callback
        self.photo_img = None

        self.emp_data = self.fetch_employee_data()
        if not self.emp_data:
            messagebox.showerror("Error", f"Employee record '{employee_id}' not found.")
            self.logout_callback()
            return

        self.create_header()

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=10)

        self.tab_profile = ttk.Frame(self.notebook)
        self.tab_leave = ttk.Frame(self.notebook)
        self.tab_att = ttk.Frame(self.notebook)
        self.tab_security = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_profile, text=" My Profile ")
        self.notebook.add(self.tab_leave, text=" Request Leave ")
        self.notebook.add(self.tab_att, text=" My Attendance ")
        self.notebook.add(self.tab_security, text=" Change Password ")

        self.build_profile_tab()
        self.build_leave_tab()
        self.build_att_tab()
        self.build_security_tab()

    def fetch_employee_data(self):
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employees WHERE employee_id=?", (self.employee_id,))
        row = cursor.fetchone()

        today_db = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("""
        SELECT COUNT(*) FROM leaves 
        WHERE employee_id=? AND status='Approved' AND ? BETWEEN start_date AND end_date
        """, (self.employee_id, today_db))
        on_leave_today = cursor.fetchone()[0] > 0
        conn.close()

        if row:
            row_list = list(row)
            if on_leave_today:
                row_list[12] = "Currently On Leave"
            return row_list
        return None

    def create_header(self):
        header = ttk.Frame(self)
        header.pack(fill="x", padx=15, pady=10)

        welcome_text = f"Welcome, {self.emp_data[1]} ({self.emp_data[0]})"
        ttk.Label(header, text=welcome_text, font=("Segoe UI", 16, "bold"), foreground="#0f172a").pack(side="left")
        ttk.Button(header, text="Logout", command=self.logout_callback, style="Destructive.TButton").pack(side="right")

    def build_profile_tab(self):
        frame = ttk.LabelFrame(self.tab_profile, text="Official Profile Details")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        photo_path = self.emp_data[14] if len(self.emp_data) > 14 else ""
        photo_lbl = ttk.Label(frame, text="[ No Photo ]", relief="solid", width=16, anchor="center")
        photo_lbl.grid(row=0, column=0, columnspan=2, padx=15, pady=10, sticky="w")

        if HAS_PIL and photo_path and os.path.exists(photo_path):
            try:
                img = Image.open(photo_path)
                img = img.resize((100, 100), Image.Resampling.LANCZOS)
                self.photo_img = ImageTk.PhotoImage(img)
                photo_lbl.config(image=self.photo_img, text="")
            except Exception:
                pass

        details = [
            ("Employee ID:", self.emp_data[0]),
            ("Full Name:", self.emp_data[1]),
            ("Gender:", self.emp_data[2]),
            ("Date of Birth:", utils.db_to_display_date(self.emp_data[3])),
            ("Email:", self.emp_data[4]),
            ("Phone:", self.emp_data[5]),
            ("Address:", self.emp_data[6]),
            ("Department:", self.emp_data[7]),
            ("Designation:", self.emp_data[8]),
            ("Joining Date:", utils.db_to_display_date(self.emp_data[9])),
            ("Employment Type:", self.emp_data[10]),
            ("Current Status:", self.emp_data[12]),
        ]

        for idx, (lbl, val) in enumerate(details, start=1):
            ttk.Label(frame, text=lbl, font=("Segoe UI", 10, "bold"), foreground="#0f172a").grid(row=idx, column=0, sticky="w", padx=15, pady=4)
            ttk.Label(frame, text=val, font=("Segoe UI", 10), foreground="#334155").grid(row=idx, column=1, sticky="w", padx=15, pady=4)

    def build_leave_tab(self):
        form_frame = ttk.LabelFrame(self.tab_leave, text="Submit Leave Application")
        form_frame.pack(fill="x", padx=15, pady=10)

        ttk.Label(form_frame, text="Leave Type:").grid(row=0, column=0, padx=8, pady=8, sticky="w")
        self.combo_ltype = ttk.Combobox(form_frame, values=["Casual", "Medical", "Annual", "Unpaid"], state="readonly", width=15)
        self.combo_ltype.set("Casual")
        self.combo_ltype.grid(row=0, column=1, padx=8, pady=8)

        ttk.Label(form_frame, text="Start Date (DD-MM-YYYY):").grid(row=0, column=2, padx=8, pady=8, sticky="w")
        self.ent_lstart = ttk.Entry(form_frame, width=15)
        self.ent_lstart.grid(row=0, column=3, padx=8, pady=8)

        ttk.Label(form_frame, text="End Date (DD-MM-YYYY):").grid(row=0, column=4, padx=8, pady=8, sticky="w")
        self.ent_lend = ttk.Entry(form_frame, width=15)
        self.ent_lend.grid(row=0, column=5, padx=8, pady=8)

        ttk.Label(form_frame, text="Reason:").grid(row=1, column=0, padx=8, pady=8, sticky="w")
        self.ent_lreason = ttk.Entry(form_frame, width=50)
        self.ent_lreason.grid(row=1, column=1, columnspan=4, padx=8, pady=8, sticky="w")

        ttk.Button(form_frame, text="Submit Request", command=self.submit_leave, style="Primary.TButton").grid(row=1, column=5, padx=8, pady=8)

        hist_frame = ttk.LabelFrame(self.tab_leave, text="My Leave History")
        hist_frame.pack(fill="both", expand=True, padx=15, pady=10)

        cols = ("id", "type", "start", "end", "days", "reason", "status")
        self.leave_table = ttk.Treeview(hist_frame, columns=cols, show="headings")

        self.leave_table.heading("id", text="ID")
        self.leave_table.heading("type", text="Type")
        self.leave_table.heading("start", text="Start Date")
        self.leave_table.heading("end", text="End Date")
        self.leave_table.heading("days", text="Days")
        self.leave_table.heading("reason", text="Reason")
        self.leave_table.heading("status", text="Status")

        for col in cols:
            self.leave_table.column(col, width=90)

        self.leave_table.tag_configure("Pending", foreground="#d97706")
        self.leave_table.tag_configure("Approved", foreground="#16a34a")
        self.leave_table.tag_configure("Rejected", foreground="#dc2626")

        self.leave_table.pack(fill="both", expand=True, padx=5, pady=5)
        self.load_my_leaves()

    def submit_leave(self):
        ltype = self.combo_ltype.get()
        start = self.ent_lstart.get().strip()
        end = self.ent_lend.get().strip()
        reason = self.ent_lreason.get().strip()

        if not (start and end and reason):
            messagebox.showerror("Error", "All fields are required.")
            return

        if not (utils.validate_date(start) and utils.validate_date(end)):
            messagebox.showerror("Error", "Dates must follow DD-MM-YYYY format.")
            return

        days = utils.calculate_inclusive_days(start, end)
        if days <= 0:
            messagebox.showerror("Error", "End date cannot be before start date.")
            return

        db_start = utils.display_to_db_date(start)
        db_end = utils.display_to_db_date(end)

        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO leaves (employee_id, leave_type, start_date, end_date, reason, status)
            VALUES (?, ?, ?, ?, ?, 'Pending')
            """, (self.employee_id, ltype, db_start, db_end, reason))
            conn.commit()
            conn.close()

            log_activity(self.employee_id, "Employee", "Submit Leave", f"Submitted {ltype} leave request ({start} to {end})")
            messagebox.showinfo("Success", f"Leave application submitted ({days} day(s)). Status: Pending.")
            self.ent_lstart.delete(0, tk.END)
            self.ent_lend.delete(0, tk.END)
            self.ent_lreason.delete(0, tk.END)
            self.load_my_leaves()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to submit leave: {e}")

    def load_my_leaves(self):
        for item in self.leave_table.get_children():
            self.leave_table.delete(item)

        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT leave_id, leave_type, start_date, end_date, reason, status FROM leaves WHERE employee_id=? ORDER BY leave_id DESC", (self.employee_id,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            self.leave_table.insert("", "end", values=("No records found", "", "", "", "", "", ""))
            return

        for row in rows:
            s_disp = utils.db_to_display_date(row[2])
            e_disp = utils.db_to_display_date(row[3])
            days = utils.calculate_inclusive_days(s_disp, e_disp)
            display_row = (row[0], row[1], s_disp, e_disp, days, row[4], f"● {row[5]}")
            self.leave_table.insert("", "end", values=display_row, tags=(row[5],))

    def build_att_tab(self):
        ctrl = ttk.Frame(self.tab_att)
        ctrl.pack(fill="x", padx=15, pady=10)

        ttk.Label(ctrl, text="Select Month (MM-YYYY):").pack(side="left", padx=5)
        self.ent_att_month = ttk.Entry(ctrl, width=12)
        self.ent_att_month.insert(0, datetime.now().strftime("%m-%Y"))
        self.ent_att_month.pack(side="left", padx=5)

        ttk.Button(ctrl, text="View Attendance", command=self.load_my_attendance, style="Primary.TButton").pack(side="left", padx=5)

        self.lbl_att_summary = ttk.Label(ctrl, text="Summary: N/A", font=("Segoe UI", 10, "bold"), foreground="#0f172a")
        self.lbl_att_summary.pack(side="right", padx=10)

        table_frame = ttk.Frame(self.tab_att)
        table_frame.pack(fill="both", expand=True, padx=15, pady=5)

        cols = ("date", "status")
        self.att_table = ttk.Treeview(table_frame, columns=cols, show="headings")
        self.att_table.heading("date", text="Date")
        self.att_table.heading("status", text="Attendance Status")

        self.att_table.tag_configure("Present", foreground="#16a34a")
        self.att_table.tag_configure("Absent", foreground="#dc2626")
        self.att_table.tag_configure("Leave", foreground="#d97706")

        self.att_table.pack(fill="both", expand=True)

        self.load_my_attendance()

    def load_my_attendance(self):
        month_str = self.ent_att_month.get().strip()
        try:
            m, y = month_str.split("-")
            month_pattern = f"{y}-{m}-%"
        except ValueError:
            messagebox.showerror("Error", "Invalid month format. Use MM-YYYY.")
            return

        for item in self.att_table.get_children():
            self.att_table.delete(item)

        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT date, status FROM attendance WHERE employee_id=? AND date LIKE ? ORDER BY date DESC", (self.employee_id, month_pattern))
        rows = cursor.fetchall()
        conn.close()

        total = len(rows)
        present = sum(1 for r in rows if r[1] == "Present")
        absent = sum(1 for r in rows if r[1] == "Absent")
        leave = sum(1 for r in rows if r[1] == "Leave")
        pct = (present / total * 100) if total > 0 else 0.0

        self.lbl_att_summary.config(text=f"Total: {total} Days | Present: {present} | Absent: {absent} | Leave: {leave} | Attendance: {pct:.2f}%")

        if not rows:
            self.att_table.insert("", "end", values=("No records found", ""))
            return

        for r in rows:
            self.att_table.insert("", "end", values=(utils.db_to_display_date(r[0]), f"● {r[1]}"), tags=(r[1],))

    def build_security_tab(self):
        frame = ttk.LabelFrame(self.tab_security, text="Security Settings")
        frame.pack(fill="x", padx=20, pady=20)

        ttk.Label(frame, text="Current Password:").grid(row=0, column=0, padx=10, pady=8, sticky="w")
        self.ent_emp_curr = ttk.Entry(frame, show="*", width=25)
        self.ent_emp_curr.grid(row=0, column=1, padx=10, pady=8)

        ttk.Label(frame, text="New Password:").grid(row=1, column=0, padx=10, pady=8, sticky="w")
        self.ent_emp_new = ttk.Entry(frame, show="*", width=25)
        self.ent_emp_new.grid(row=1, column=1, padx=10, pady=8)

        ttk.Button(frame, text="Change Password", command=self.change_password, style="Primary.TButton").grid(row=2, column=0, columnspan=2, pady=15)

    def change_password(self):
        curr = self.ent_emp_curr.get().strip()
        new_p = self.ent_emp_new.get().strip()

        if not curr or not new_p:
            messagebox.showerror("Error", "All password fields are required.")
            return

        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM employees WHERE employee_id=?", (self.employee_id,))
        stored_hash = cursor.fetchone()[0]

        if not utils.verify_password(stored_hash, curr):
            messagebox.showerror("Error", "Incorrect current password.")
            conn.close()
            return

        new_hash = utils.hash_password(new_p)
        cursor.execute("UPDATE employees SET password_hash=? WHERE employee_id=?", (new_hash, self.employee_id))
        conn.commit()
        conn.close()

        log_activity(self.employee_id, "Employee", "Change Password", "Employee updated password successfully.")
        messagebox.showinfo("Success", "Your password has been changed successfully.")
        self.ent_emp_curr.delete(0, tk.END)
        self.ent_emp_new.delete(0, tk.END)
