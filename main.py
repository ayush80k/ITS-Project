import tkinter as tk
from tkinter import ttk, messagebox
import database
import utils
from activity_logger import log_activity
from dashboard import DashboardView
from employee import EmployeeView
from attendance import AttendanceView
from leave import LeaveView
from activity_log_view import ActivityLogView
from settings import SettingsView
from employee_portal import EmployeePortalView

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Employee Management System")
        self.geometry("1100x680")
        self.minsize(980, 580)
        self.configure(bg="#f8fafc")

        database.init_db()
        self.setup_global_styles()

        self.sidebar_buttons = {}
        self.active_view = None

        self.show_portal_selection()

    def setup_global_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        # Global Colors
        BG_COLOR = "#f8fafc"
        NAVY_DARK = "#0f172a"
        PRIMARY_BLUE = "#2563eb"
        PRIMARY_HOVER = "#1d4ed8"
        SECONDARY_GRAY = "#e2e8f0"
        TEXT_DARK = "#0f172a"

        style.configure(".", background=BG_COLOR, font=("Segoe UI", 9))
        style.configure("TFrame", background=BG_COLOR)
        style.configure("TLabelframe", background="#ffffff", bordercolor="#cbd5e1", borderwidth=1, relief="solid")
        style.configure("TLabelframe.Label", font=("Segoe UI", 10, "bold"), foreground=TEXT_DARK, background="#ffffff")

        # Buttons
        style.configure("Primary.TButton", font=("Segoe UI", 9, "bold"), background=PRIMARY_BLUE, foreground="#ffffff", borderwidth=0, padding=6)
        style.map("Primary.TButton", background=[("active", PRIMARY_HOVER)])

        style.configure("Secondary.TButton", font=("Segoe UI", 9), background=SECONDARY_GRAY, foreground=TEXT_DARK, borderwidth=0, padding=6)
        style.map("Secondary.TButton", background=[("active", "#cbd5e1")])

        style.configure("Success.TButton", font=("Segoe UI", 9, "bold"), background="#16a34a", foreground="#ffffff", borderwidth=0, padding=6)
        style.map("Success.TButton", background=[("active", "#15803d")])

        style.configure("Destructive.TButton", font=("Segoe UI", 9, "bold"), background="#dc2626", foreground="#ffffff", borderwidth=0, padding=6)
        style.map("Destructive.TButton", background=[("active", "#b91c1c")])

        # Sidebar Buttons
        style.configure("Sidebar.TButton", font=("Segoe UI", 10), background=NAVY_DARK, foreground="#94a3b8", borderwidth=0, padding=8, anchor="w")
        style.map("Sidebar.TButton", background=[("active", "#1e293b")], foreground=[("active", "#ffffff")])

        style.configure("ActiveSidebar.TButton", font=("Segoe UI", 10, "bold"), background=PRIMARY_BLUE, foreground="#ffffff", borderwidth=0, padding=8, anchor="w")
        style.map("ActiveSidebar.TButton", background=[("active", PRIMARY_HOVER)])

        style.configure("SidebarLogout.TButton", font=("Segoe UI", 10, "bold"), background="#dc2626", foreground="#ffffff", borderwidth=0, padding=8, anchor="w")
        style.map("SidebarLogout.TButton", background=[("active", "#b91c1c")])

        # Treeview / Tables
        style.configure("Treeview", background="#ffffff", fieldbackground="#ffffff", foreground="#1e293b", rowheight=26, borderwidth=1, relief="solid")
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"), background="#f1f5f9", foreground="#0f172a", borderwidth=1)
        style.map("Treeview", background=[("selected", "#dbeafe")], foreground=[("selected", "#1e3a8a")])

        # Notebook
        style.configure("TNotebook", background=BG_COLOR, borderwidth=0)
        style.configure("TNotebook.Tab", font=("Segoe UI", 9, "bold"), padding=[12, 6], background="#e2e8f0", foreground="#475569")
        style.map("TNotebook.Tab", background=[("selected", "#ffffff")], foreground=[("selected", PRIMARY_BLUE)])

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_portal_selection(self):
        self.clear_window()

        container = ttk.Frame(self)
        container.pack(expand=True)

        title = ttk.Label(container, text="Employee Management System", font=("Segoe UI", 22, "bold"), foreground="#0f172a")
        title.pack(pady=15)

        notebook = ttk.Notebook(container)
        notebook.pack(padx=20, pady=10)

        # Tab 1: Admin Login
        tab_admin = ttk.Frame(notebook, padding=15)
        notebook.add(tab_admin, text=" Admin Login ")

        ttk.Label(tab_admin, text="Username:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.ent_admin_user = ttk.Entry(tab_admin, width=25)
        self.ent_admin_user.insert(0, "admin")
        self.ent_admin_user.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(tab_admin, text="Password:", font=("Segoe UI", 9, "bold")).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.ent_admin_pass = ttk.Entry(tab_admin, show="*", width=25)
        self.ent_admin_pass.insert(0, "admin123")
        self.ent_admin_pass.grid(row=1, column=1, padx=10, pady=10)

        ttk.Button(tab_admin, text="Login as Admin", command=self.verify_admin_login, style="Primary.TButton").grid(row=2, column=0, columnspan=2, pady=15)

        # Tab 2: Employee Login
        tab_emp = ttk.Frame(notebook, padding=15)
        notebook.add(tab_emp, text=" Employee Login ")

        ttk.Label(tab_emp, text="Employee ID:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.ent_emp_id = ttk.Entry(tab_emp, width=25)
        self.ent_emp_id.insert(0, "EMP001")
        self.ent_emp_id.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(tab_emp, text="Password:", font=("Segoe UI", 9, "bold")).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.ent_emp_pass = ttk.Entry(tab_emp, show="*", width=25)
        self.ent_emp_pass.insert(0, "emp123")
        self.ent_emp_pass.grid(row=1, column=1, padx=10, pady=10)

        ttk.Button(tab_emp, text="Login as Employee", command=self.verify_employee_login, style="Primary.TButton").grid(row=2, column=0, columnspan=2, pady=15)

    def verify_admin_login(self):
        user = self.ent_admin_user.get().strip()
        pwd = self.ent_admin_pass.get().strip()

        if not user or not pwd:
            messagebox.showerror("Login Error", "Please fill in all username and password fields.")
            return

        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE username=? AND role='Admin'", (user,))
        row = cursor.fetchone()
        conn.close()

        if row and utils.verify_password(row[0], pwd):
            log_activity(user, "Admin", "Admin Login", "Admin logged in successfully.")
            self.open_admin_portal()
        else:
            log_activity(user, "Admin", "Failed Login", "Invalid admin credentials attempt.")
            messagebox.showerror("Authentication Failed", "Invalid Admin Username or Password.")

    def verify_employee_login(self):
        emp_id = self.ent_emp_id.get().strip()
        pwd = self.ent_emp_pass.get().strip()

        if not emp_id or not pwd:
            messagebox.showerror("Login Error", "Please enter both Employee ID and Password.")
            return

        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash, status FROM employees WHERE employee_id=?", (emp_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            messagebox.showerror("Authentication Failed", f"Employee ID '{emp_id}' not found.")
            return

        stored_hash, status = row
        if status == "Inactive":
            messagebox.showerror("Access Denied", "Your employee account is currently marked Inactive.")
            return

        if utils.verify_password(stored_hash, pwd):
            log_activity(emp_id, "Employee", "Employee Login", f"Employee {emp_id} logged in successfully.")
            self.open_employee_portal(emp_id)
        else:
            log_activity(emp_id, "Employee", "Failed Login", f"Failed login attempt for {emp_id}")
            messagebox.showerror("Authentication Failed", "Invalid Employee Password.")

    def open_admin_portal(self):
        self.clear_window()

        self.sidebar = tk.Frame(self, bg="#0f172a", width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.content_container = ttk.Frame(self)
        self.content_container.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.setup_admin_sidebar()
        self.show_admin_view("Dashboard")

    def setup_admin_sidebar(self):
        title_lbl = tk.Label(self.sidebar, text="Admin Control", font=("Segoe UI", 14, "bold"), bg="#0f172a", fg="#ffffff")
        title_lbl.pack(padx=15, pady=(20, 25), anchor="w")

        nav_items = [
            ("Dashboard", "Dashboard"),
            ("Employee Directory", "Employees"),
            ("Attendance Manager", "Attendance"),
            ("Leave Approvals", "Leave"),
            ("Activity / Audit Log", "ActivityLog"),
            ("System Settings", "Settings")
        ]

        self.sidebar_buttons = {}

        for text, view_key in nav_items:
            btn = ttk.Button(
                self.sidebar, 
                text=f"  {text}", 
                command=lambda vk=view_key: self.show_admin_view(vk), 
                style="Sidebar.TButton"
            )
            btn.pack(fill="x", padx=10, pady=3)
            self.sidebar_buttons[view_key] = btn

        # Logout button at bottom
        logout_btn = ttk.Button(
            self.sidebar, 
            text="  Logout Admin", 
            command=self.show_portal_selection, 
            style="SidebarLogout.TButton"
        )
        logout_btn.pack(side="bottom", fill="x", padx=10, pady=20)

    def show_admin_view(self, view_name):
        for widget in self.content_container.winfo_children():
            widget.pack_forget()

        # Update Sidebar Active Item Highlighting
        for key, btn in self.sidebar_buttons.items():
            if key == view_name:
                btn.config(style="ActiveSidebar.TButton")
            else:
                btn.config(style="Sidebar.TButton")

        if view_name == "Dashboard":
            view = DashboardView(self.content_container)
        elif view_name == "Employees":
            view = EmployeeView(self.content_container)
        elif view_name == "Attendance":
            view = AttendanceView(self.content_container)
        elif view_name == "Leave":
            view = LeaveView(self.content_container)
        elif view_name == "ActivityLog":
            view = ActivityLogView(self.content_container)
        elif view_name == "Settings":
            view = SettingsView(self.content_container)

        view.pack(fill="both", expand=True)

    def open_employee_portal(self, emp_id):
        self.clear_window()
        EmployeePortalView(self, emp_id, self.show_portal_selection)

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
