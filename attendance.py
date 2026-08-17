import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import database
import utils
from activity_logger import log_activity

class AttendanceView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill="both", expand=True)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_daily = ttk.Frame(self.notebook)
        self.tab_report = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_daily, text=" Daily Attendance Manager ")
        self.notebook.add(self.tab_report, text=" Attendance Report & Export ")

        self.employee_rows = {}
        self.build_daily_tab()
        self.build_report_tab()

    def build_daily_tab(self):
        ctrl_frame = ttk.LabelFrame(self.tab_daily, text="Select Date & Department")
        ctrl_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(ctrl_frame, text="Date (DD-MM-YYYY):").grid(row=0, column=0, padx=5, pady=10)
        self.ent_date = ttk.Entry(ctrl_frame, width=15)
        self.ent_date.insert(0, utils.db_to_display_date(datetime.now().strftime('%Y-%m-%d')))
        self.ent_date.grid(row=0, column=1, padx=5, pady=10)

        ttk.Label(ctrl_frame, text="Department:").grid(row=0, column=2, padx=5, pady=10)
        self.combo_dept = ttk.Combobox(ctrl_frame, values=["All", "Software Development", "Human Resources", "Marketing", "Finance", "Sales", "Administration"], state="readonly", width=18)
        self.combo_dept.set("All")
        self.combo_dept.grid(row=0, column=3, padx=5, pady=10)

        ttk.Button(ctrl_frame, text="Load Staff List", command=self.load_daily_grid, style="Primary.TButton").grid(row=0, column=4, padx=10, pady=10)

        legend_frame = ttk.Frame(self.tab_daily)
        legend_frame.pack(fill="x", padx=10, pady=2)

        ttk.Label(legend_frame, text="Status Legend:", font=("Segoe UI", 9, "bold"), foreground="#0f172a").pack(side="left", padx=(0, 10))
        ttk.Label(legend_frame, text="● Present", font=("Segoe UI", 9, "bold"), foreground="#16a34a").pack(side="left", padx=5)
        ttk.Label(legend_frame, text="● Absent", font=("Segoe UI", 9, "bold"), foreground="#dc2626").pack(side="left", padx=5)
        ttk.Label(legend_frame, text="● Leave", font=("Segoe UI", 9, "bold"), foreground="#d97706").pack(side="left", padx=5)

        ttk.Button(legend_frame, text="Save Attendance", command=self.save_daily_attendance, style="Primary.TButton").pack(side="right", padx=5)
        ttk.Button(legend_frame, text="Mark All Present", command=self.mark_all_present, style="Secondary.TButton").pack(side="right", padx=5)

        container = ttk.Frame(self.tab_daily)
        container.pack(fill="both", expand=True, padx=10, pady=5)

        canvas = tk.Canvas(container, bg="#ffffff", highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.scroll_frame = ttk.Frame(canvas)

        self.scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load_daily_grid(self):
        date_str = self.ent_date.get().strip()
        db_date = utils.display_to_db_date(date_str)
        if not db_date:
            messagebox.showerror("Error", "Invalid Date format. Use DD-MM-YYYY.")
            return

        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        self.employee_rows = {}

        ttk.Label(self.scroll_frame, text="Emp ID", font=("Segoe UI", 9, "bold"), width=12, foreground="#0f172a").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ttk.Label(self.scroll_frame, text="Name", font=("Segoe UI", 9, "bold"), width=25, foreground="#0f172a").grid(row=0, column=1, padx=10, pady=5, sticky="w")
        ttk.Label(self.scroll_frame, text="Department", font=("Segoe UI", 9, "bold"), width=20, foreground="#0f172a").grid(row=0, column=2, padx=10, pady=5, sticky="w")
        ttk.Label(self.scroll_frame, text="Attendance Status", font=("Segoe UI", 9, "bold"), width=18, foreground="#0f172a").grid(row=0, column=3, padx=10, pady=5, sticky="w")

        dept_filter = self.combo_dept.get()

        conn = database.get_connection()
        cursor = conn.cursor()

        query = "SELECT employee_id, name, department FROM employees WHERE status='Active'"
        params = []
        if dept_filter != "All":
            query += " AND department=?"
            params.append(dept_filter)

        cursor.execute(query, params)
        emps = cursor.fetchall()

        cursor.execute("SELECT employee_id, status FROM attendance WHERE date=?", (db_date,))
        existing_att = dict(cursor.fetchall())

        cursor.execute("SELECT DISTINCT employee_id FROM leaves WHERE status='Approved' AND ? BETWEEN start_date AND end_date", (db_date,))
        approved_leave_emps = set(r[0] for r in cursor.fetchall())

        conn.close()

        if not emps:
            ttk.Label(self.scroll_frame, text="No active employees found.", font=("Segoe UI", 10, "italic")).grid(row=1, column=0, columnspan=4, padx=10, pady=10)
            return

        for idx, emp in enumerate(emps, start=1):
            emp_id, name, dept = emp
            ttk.Label(self.scroll_frame, text=emp_id, width=12).grid(row=idx, column=0, padx=10, pady=4, sticky="w")
            ttk.Label(self.scroll_frame, text=name, width=25).grid(row=idx, column=1, padx=10, pady=4, sticky="w")
            ttk.Label(self.scroll_frame, text=dept, width=20).grid(row=idx, column=2, padx=10, pady=4, sticky="w")

            combo = ttk.Combobox(self.scroll_frame, values=["Present", "Absent", "Leave"], state="readonly", width=15)
            
            if emp_id in approved_leave_emps:
                initial_val = "Leave"
            else:
                initial_val = existing_att.get(emp_id, "Present")
                
            combo.set(initial_val)
            combo.grid(row=idx, column=3, padx=10, pady=4, sticky="w")

            self.employee_rows[emp_id] = combo

    def mark_all_present(self):
        for combo in self.employee_rows.values():
            combo.set("Present")

    def save_daily_attendance(self):
        date_str = self.ent_date.get().strip()
        db_date = utils.display_to_db_date(date_str)
        if not db_date or not self.employee_rows:
            messagebox.showerror("Error", "Please load employees with a valid date first.")
            return

        try:
            conn = database.get_connection()
            cursor = conn.cursor()

            for emp_id, combo in self.employee_rows.items():
                status = combo.get()
                cursor.execute("""
                INSERT INTO attendance (employee_id, date, status)
                VALUES (?, ?, ?)
                ON CONFLICT(employee_id, date) DO UPDATE SET status=excluded.status
                """, (emp_id, db_date, status))

            conn.commit()
            conn.close()

            log_activity("ADMIN", "Admin", "Mark Attendance", f"Saved batch attendance for {len(self.employee_rows)} staff on {date_str}")
            messagebox.showinfo("Success", f"Attendance recorded successfully for {date_str}.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save attendance: {e}")

    def build_report_tab(self):
        filter_frame = ttk.LabelFrame(self.tab_report, text="Report Parameters")
        filter_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(filter_frame, text="Month (MM-YYYY):").grid(row=0, column=0, padx=5, pady=5)
        self.ent_rep_month = ttk.Entry(filter_frame, width=12)
        self.ent_rep_month.insert(0, datetime.now().strftime("%m-%Y"))
        self.ent_rep_month.grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(filter_frame, text="Generate Report", command=self.generate_report, style="Primary.TButton").grid(row=0, column=2, padx=10, pady=5)
        ttk.Button(filter_frame, text="Export to CSV", command=self.export_csv, style="Secondary.TButton").grid(row=0, column=3, padx=10, pady=5)

        table_frame = ttk.Frame(self.tab_report)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("emp_id", "name", "dept", "working_days", "present", "absent", "leave", "percentage")
        self.report_table = ttk.Treeview(table_frame, columns=columns, show="headings")

        self.report_table.heading("emp_id", text="Emp ID")
        self.report_table.heading("name", text="Name")
        self.report_table.heading("dept", text="Department")
        self.report_table.heading("working_days", text="Total Days")
        self.report_table.heading("present", text="Present")
        self.report_table.heading("absent", text="Absent")
        self.report_table.heading("leave", text="Leave")
        self.report_table.heading("percentage", text="Attendance %")

        for col in columns:
            self.report_table.column(col, width=110)

        self.report_table.pack(fill="both", expand=True)

    def generate_report(self):
        month_str = self.ent_rep_month.get().strip()
        try:
            m, y = month_str.split("-")
            month_pattern = f"{y}-{m}-%"
        except ValueError:
            messagebox.showerror("Error", "Invalid month format. Use MM-YYYY.")
            return

        for item in self.report_table.get_children():
            self.report_table.delete(item)

        conn = database.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT employee_id, name, department FROM employees WHERE status='Active'")
        employees = cursor.fetchall()

        if not employees:
            self.report_table.insert("", "end", values=("No records found", "", "", "", "", "", "", ""))
            conn.close()
            return

        for emp in employees:
            emp_id, name, dept = emp
            cursor.execute("SELECT status FROM attendance WHERE employee_id=? AND date LIKE ?", (emp_id, month_pattern))
            records = [r[0] for r in cursor.fetchall()]

            total_days = len(records)
            present = records.count("Present")
            absent = records.count("Absent")
            leave = records.count("Leave")
            pct = f"{(present / total_days * 100):.2f}%" if total_days > 0 else "N/A"

            self.report_table.insert("", "end", values=(emp_id, name, dept, total_days, present, absent, leave, pct))

        conn.close()

    def export_csv(self):
        if not self.report_table.get_children():
            messagebox.showwarning("Warning", "No report data available to export.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            title="Export Attendance Report"
        )
        if not file_path:
            return

        try:
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Employee ID", "Name", "Department", "Total Days", "Present", "Absent", "Leave", "Attendance %"])
                for row_id in self.report_table.get_children():
                    writer.writerow(self.report_table.item(row_id)['values'])
            messagebox.showinfo("Success", f"Report exported successfully to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export CSV: {e}")
