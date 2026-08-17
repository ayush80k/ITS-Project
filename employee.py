import os
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import database
import utils
from activity_logger import log_activity

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

DEPARTMENTS = ["Software Development", "Human Resources", "Marketing", "Finance", "Sales", "Administration"]
EMP_TYPES = ["Full-Time", "Part-Time", "Contract", "Intern"]
STATUSES = ["Active", "Inactive"]

class EmployeeDetailsModal(tk.Toplevel):
    def __init__(self, parent, emp_data):
        super().__init__(parent)
        self.title(f"Employee Profile — {emp_data['name']} ({emp_data['id']})")
        self.geometry("450x550")
        self.configure(bg="#ffffff")
        self.resizable(False, False)
        self.grab_set()

        container = ttk.Frame(self, padding=15)
        container.pack(fill="both", expand=True)

        ttk.Label(container, text="EMPLOYEE PROFILE CARD", font=("Segoe UI", 12, "bold"), foreground="#0f172a").pack(pady=(0, 10))

        header_frame = ttk.Frame(container)
        header_frame.pack(fill="x", pady=10)

        photo_lbl = ttk.Label(header_frame, text="[ No Photo ]", relief="solid", width=14, anchor="center")
        photo_lbl.pack(side="left", padx=(0, 15))

        if HAS_PIL and emp_data['photo_path'] and os.path.exists(emp_data['photo_path']):
            try:
                img = Image.open(emp_data['photo_path'])
                img = img.resize((90, 90), Image.Resampling.LANCZOS)
                self.photo_img = ImageTk.PhotoImage(img)
                photo_lbl.config(image=self.photo_img, text="")
            except Exception:
                pass

        meta_frame = ttk.Frame(header_frame)
        meta_frame.pack(side="left", fill="both", expand=True)

        ttk.Label(meta_frame, text=emp_data['name'], font=("Segoe UI", 13, "bold"), foreground="#0f172a").pack(anchor="w")
        ttk.Label(meta_frame, text=f"ID: {emp_data['id']}", font=("Segoe UI", 9, "italic"), foreground="#64748b").pack(anchor="w")
        ttk.Label(meta_frame, text=f"{emp_data['desig']} • {emp_data['dept']}", font=("Segoe UI", 9), foreground="#334155").pack(anchor="w", pady=(2, 0))

        status_text = "● Active" if emp_data['status'] == "Active" else "● Inactive"
        status_color = "#16a34a" if emp_data['status'] == "Active" else "#dc2626"
        ttk.Label(meta_frame, text=f"Status: {status_text}", font=("Segoe UI", 9, "bold"), foreground=status_color).pack(anchor="w", pady=(2, 0))

        ttk.Separator(container, orient="horizontal").pack(fill="x", pady=10)

        info_frame = ttk.Frame(container)
        info_frame.pack(fill="both", expand=True)

        details = [
            ("Gender:", emp_data['gender']),
            ("Date of Birth:", utils.db_to_display_date(emp_data['dob'])),
            ("Email:", emp_data['email']),
            ("Phone:", emp_data['phone']),
            ("Address:", emp_data['address']),
            ("Employment Type:", emp_data['type']),
            ("Joining Date:", utils.db_to_display_date(emp_data['joining'])),
            ("Salary:", f"₹ {float(emp_data['salary']):,.2f}")
        ]

        for idx, (label, value) in enumerate(details):
            ttk.Label(info_frame, text=label, font=("Segoe UI", 9, "bold"), foreground="#0f172a").grid(row=idx, column=0, sticky="w", pady=3)
            ttk.Label(info_frame, text=value, font=("Segoe UI", 9), foreground="#334155").grid(row=idx, column=1, sticky="w", padx=10, pady=3)

        ttk.Button(container, text="Close", command=self.destroy, style="Secondary.TButton").pack(pady=(15, 0))


class EmployeeFormModal(tk.Toplevel):
    def __init__(self, parent, emp_data=None, on_save_callback=None):
        super().__init__(parent)
        self.is_edit = emp_data is not None
        self.on_save_callback = on_save_callback

        title_text = f"Edit Employee — {emp_data['id']}" if self.is_edit else "Add New Employee"
        self.title(title_text)
        self.geometry("450x620")
        self.configure(bg="#ffffff")
        self.resizable(False, False)
        self.grab_set()

        self.existing_photo_path = emp_data.get('photo_path', '') if emp_data else ''
        self.newly_selected_photo_path = ''
        self.photo_img = None

        container = ttk.Frame(self, padding=15)
        container.pack(fill="both", expand=True)

        ttk.Label(container, text=title_text, font=("Segoe UI", 13, "bold"), foreground="#0f172a").pack(pady=(0, 10))

        photo_frame = ttk.Frame(container)
        photo_frame.pack(fill="x", pady=5)
        self.lbl_photo_preview = ttk.Label(photo_frame, text="[ No Image ]", relief="solid", width=14, anchor="center")
        self.lbl_photo_preview.pack(side="left", padx=(0, 10))
        ttk.Button(photo_frame, text="Upload Photo", command=self.upload_photo, style="Secondary.TButton").pack(side="left")

        if self.existing_photo_path:
            self.display_image(self.existing_photo_path)

        form_frame = ttk.Frame(container)
        form_frame.pack(fill="both", expand=True, pady=10)

        fields = [
            ("Employee ID*:", "ent_id"),
            ("Full Name*:", "ent_name"),
            ("Gender*:", "combo_gender"),
            ("DOB (DD-MM-YYYY)*:", "ent_dob"),
            ("Email*:", "ent_email"),
            ("Phone Number*:", "ent_phone"),
            ("Address*:", "ent_address"),
            ("Department*:", "combo_dept"),
            ("Designation*:", "ent_desig"),
            ("Joining Date (DD-MM-YYYY)*:", "ent_joining"),
            ("Employment Type*:", "combo_type"),
            ("Salary*:", "ent_salary"),
            ("Status*:", "combo_status")
        ]

        self.inputs = {}
        for idx, (label_text, var_name) in enumerate(fields):
            lbl = ttk.Label(form_frame, text=label_text)
            lbl.grid(row=idx, column=0, sticky="w", pady=2)

            if "combo_gender" in var_name:
                widget = ttk.Combobox(form_frame, values=["Male", "Female", "Other"], state="readonly", width=25)
            elif "combo_dept" in var_name:
                widget = ttk.Combobox(form_frame, values=DEPARTMENTS, state="readonly", width=25)
            elif "combo_type" in var_name:
                widget = ttk.Combobox(form_frame, values=EMP_TYPES, state="readonly", width=25)
            elif "combo_status" in var_name:
                widget = ttk.Combobox(form_frame, values=STATUSES, state="readonly", width=25)
                widget.set("Active")
            else:
                widget = ttk.Entry(form_frame, width=27)

            widget.grid(row=idx, column=1, padx=5, pady=2)
            self.inputs[var_name] = widget

        if self.is_edit and emp_data:
            self.inputs["ent_id"].insert(0, emp_data['id'])
            self.inputs["ent_id"].config(state="disabled")
            self.inputs["ent_name"].insert(0, emp_data['name'])
            self.inputs["combo_gender"].set(emp_data['gender'])
            self.inputs["ent_dob"].insert(0, utils.db_to_display_date(emp_data['dob']))
            self.inputs["ent_email"].insert(0, emp_data['email'])
            self.inputs["ent_phone"].insert(0, emp_data['phone'])
            self.inputs["ent_address"].insert(0, emp_data['address'])
            self.inputs["combo_dept"].set(emp_data['dept'])
            self.inputs["ent_desig"].insert(0, emp_data['desig'])
            self.inputs["ent_joining"].insert(0, utils.db_to_display_date(emp_data['joining']))
            self.inputs["combo_type"].set(emp_data['type'])
            self.inputs["ent_salary"].insert(0, str(emp_data['salary']))
            self.inputs["combo_status"].set(emp_data['status'])

        btn_frame = ttk.Frame(container)
        btn_frame.pack(fill="x", pady=10)

        ttk.Button(btn_frame, text="Save Record", command=self.save_employee, style="Primary.TButton").pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy, style="Secondary.TButton").pack(side="right", padx=5)

    def display_image(self, path):
        if HAS_PIL and path and os.path.exists(path):
            try:
                img = Image.open(path)
                img = img.resize((75, 75), Image.Resampling.LANCZOS)
                self.photo_img = ImageTk.PhotoImage(img)
                self.lbl_photo_preview.config(image=self.photo_img, text="")
                return
            except Exception:
                pass
        self.lbl_photo_preview.config(image="", text="[ No Image ]")

    def upload_photo(self):
        file_path = filedialog.askopenfilename(
            title="Select Profile Photo",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png")]
        )
        if file_path:
            self.newly_selected_photo_path = file_path
            self.display_image(file_path)

    def process_photo_save(self, emp_id):
        if not self.newly_selected_photo_path or not os.path.exists(self.newly_selected_photo_path):
            return self.existing_photo_path

        dest_dir = utils.resource_path("assets/employee_photos")
        os.makedirs(dest_dir, exist_ok=True)
        ext = os.path.splitext(self.newly_selected_photo_path)[1]
        dest_path = os.path.join(dest_dir, f"{emp_id}{ext}")

        src_abs = os.path.abspath(self.newly_selected_photo_path)
        dst_abs = os.path.abspath(dest_path)

        if src_abs != dst_abs:
            shutil.copy2(self.newly_selected_photo_path, dest_path)

        return dest_path

    def save_employee(self):
        emp_id = self.inputs["ent_id"].get().strip()
        name = self.inputs["ent_name"].get().strip()
        gender = self.inputs["combo_gender"].get().strip()
        dob = self.inputs["ent_dob"].get().strip()
        email = self.inputs["ent_email"].get().strip()
        phone = self.inputs["ent_phone"].get().strip()
        address = self.inputs["ent_address"].get().strip()
        dept = self.inputs["combo_dept"].get().strip()
        desig = self.inputs["ent_desig"].get().strip()
        joining = self.inputs["ent_joining"].get().strip()
        type_val = self.inputs["combo_type"].get().strip()
        salary = self.inputs["ent_salary"].get().strip()
        status = self.inputs["combo_status"].get().strip()

        if not (emp_id and name and gender and dob and email and phone and address and dept and desig and joining and type_val and salary and status):
            messagebox.showerror("Validation Error", "All fields are required.", parent=self)
            return

        if not utils.validate_email(email):
            messagebox.showerror("Validation Error", "Please enter a valid email address.", parent=self)
            return

        if not utils.validate_phone(phone):
            messagebox.showerror("Validation Error", "Phone number must be exactly 10 digits.", parent=self)
            return

        if not (utils.validate_date(dob) and utils.validate_date(joining)):
            messagebox.showerror("Validation Error", "Dates must follow DD-MM-YYYY format.", parent=self)
            return

        if not utils.validate_number(salary):
            messagebox.showerror("Validation Error", "Salary must be a valid numeric amount.", parent=self)
            return

        db_dob = utils.display_to_db_date(dob)
        db_joining = utils.display_to_db_date(joining)
        photo_saved_path = self.process_photo_save(emp_id)

        try:
            conn = database.get_connection()
            cursor = conn.cursor()

            if self.is_edit:
                cursor.execute("""
                UPDATE employees SET name=?, gender=?, dob=?, email=?, phone=?, address=?, department=?, designation=?, joining_date=?, employment_type=?, salary=?, status=?, photo_path=?
                WHERE employee_id=?
                """, (name, gender, db_dob, email, phone, address, dept, desig, db_joining, type_val, float(salary), status, photo_saved_path, emp_id))
                action_text = "Update Employee"
                desc_text = f"Updated employee profile for {name} ({emp_id})"
                msg_text = "Employee updated successfully."
            else:
                default_pwd_hash = utils.hash_password("emp123")
                cursor.execute("""
                INSERT INTO employees (employee_id, name, gender, dob, email, phone, address, department, designation, joining_date, employment_type, salary, status, password_hash, photo_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (emp_id, name, gender, db_dob, email, phone, address, dept, desig, db_joining, type_val, float(salary), status, default_pwd_hash, photo_saved_path))
                action_text = "Add Employee"
                desc_text = f"Created employee profile for {name} ({emp_id})"
                msg_text = f"Employee added successfully! Default Password: emp123"

            conn.commit()
            conn.close()

            log_activity("ADMIN", "Admin", action_text, desc_text)
            messagebox.showinfo("Success", msg_text, parent=self)
            if self.on_save_callback:
                self.on_save_callback()
            self.destroy()

        except database.sqlite3.IntegrityError:
            messagebox.showerror("Database Error", f"Employee ID '{emp_id}' already exists.", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save employee: {e}", parent=self)


class EmployeeView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill="both", expand=True)

        self.selected_emp_id = None
        self.create_widgets()
        self.load_employees()

    def create_widgets(self):
        header = ttk.Frame(self)
        header.pack(fill="x", padx=15, pady=(15, 10))

        ttk.Label(header, text="Employee Directory", font=("Segoe UI", 16, "bold"), foreground="#0f172a").pack(side="left")
        ttk.Button(header, text="➕ Add New Employee", command=self.open_add_dialog, style="Primary.TButton").pack(side="right")

        search_bar = ttk.LabelFrame(self, text="Search & Filters")
        search_bar.pack(fill="x", padx=15, pady=(0, 5))

        ttk.Label(search_bar, text="Search:").pack(side="left", padx=5)
        self.ent_search = ttk.Entry(search_bar, width=20)
        self.ent_search.pack(side="left", padx=5, pady=5)

        ttk.Label(search_bar, text="Dept:").pack(side="left", padx=5)
        self.combo_filter_dept = ttk.Combobox(search_bar, values=["All"] + DEPARTMENTS, state="readonly", width=15)
        self.combo_filter_dept.set("All")
        self.combo_filter_dept.pack(side="left", padx=5)

        ttk.Label(search_bar, text="Status:").pack(side="left", padx=5)
        self.combo_filter_status = ttk.Combobox(search_bar, values=["All"] + STATUSES, state="readonly", width=10)
        self.combo_filter_status.set("All")
        self.combo_filter_status.pack(side="left", padx=5)

        ttk.Button(search_bar, text="Apply Filter", command=self.load_employees, style="Secondary.TButton").pack(side="left", padx=5)
        ttk.Button(search_bar, text="Reset", command=self.reset_search, style="Secondary.TButton").pack(side="left", padx=5)

        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=15, pady=5)

        columns = ("id", "name", "dept", "desig", "phone", "joining", "status")
        self.table = ttk.Treeview(table_frame, columns=columns, show="headings")

        self.table.heading("id", text="ID")
        self.table.heading("name", text="Name")
        self.table.heading("dept", text="Department")
        self.table.heading("desig", text="Designation")
        self.table.heading("phone", text="Phone")
        self.table.heading("joining", text="Joining Date")
        self.table.heading("status", text="Status")

        for col in columns:
            self.table.column(col, width=110)

        self.table.tag_configure("Active", foreground="#16a34a")
        self.table.tag_configure("Inactive", foreground="#dc2626")

        self.table.pack(fill="both", expand=True, side="left")
        self.table.bind("<<TreeviewSelect>>", self.on_select_row)

        action_bar = ttk.Frame(self)
        action_bar.pack(fill="x", padx=15, pady=10)

        ttk.Button(action_bar, text="👁 View Details", command=self.open_view_details, style="Secondary.TButton").pack(side="left", padx=5)
        ttk.Button(action_bar, text="✎ Edit Employee", command=self.open_edit_dialog, style="Primary.TButton").pack(side="left", padx=5)
        ttk.Button(action_bar, text="🔑 Set Password", command=self.open_password_dialog, style="Secondary.TButton").pack(side="left", padx=5)
        ttk.Button(action_bar, text="🗑 Delete Employee", command=self.delete_employee, style="Destructive.TButton").pack(side="right", padx=5)

    def on_select_row(self, event):
        selected_item = self.table.selection()
        if selected_item:
            values = self.table.item(selected_item[0])['values']
            if values and str(values[0]) != "No records found":
                self.selected_emp_id = str(values[0])

    def fetch_full_emp_data(self, emp_id):
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employees WHERE employee_id=?", (emp_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "id": row[0], "name": row[1], "gender": row[2], "dob": row[3],
                "email": row[4], "phone": row[5], "address": row[6], "dept": row[7],
                "desig": row[8], "joining": row[9], "type": row[10], "salary": row[11],
                "status": row[12], "photo_path": row[14] if len(row) > 14 else ""
            }
        return None

    def open_view_details(self):
        if not self.selected_emp_id:
            messagebox.showwarning("Selection Required", "Please select an employee from the table first.")
            return
        data = self.fetch_full_emp_data(self.selected_emp_id)
        if data:
            EmployeeDetailsModal(self, data)

    def open_add_dialog(self):
        EmployeeFormModal(self, emp_data=None, on_save_callback=self.load_employees)

    def open_edit_dialog(self):
        if not self.selected_emp_id:
            messagebox.showwarning("Selection Required", "Please select an employee from the table first.")
            return
        data = self.fetch_full_emp_data(self.selected_emp_id)
        if data:
            EmployeeFormModal(self, emp_data=data, on_save_callback=self.load_employees)

    def open_password_dialog(self):
        if not self.selected_emp_id:
            messagebox.showwarning("Selection Required", "Please select an employee to set password.")
            return

        dialog = tk.Toplevel(self)
        dialog.title(f"Set Password for {self.selected_emp_id}")
        dialog.geometry("320x160")
        dialog.configure(bg="#ffffff")
        dialog.grab_set()

        ttk.Label(dialog, text=f"New Password for {self.selected_emp_id}:", font=("Segoe UI", 10)).pack(pady=10)
        ent_pwd = ttk.Entry(dialog, show="*", width=25)
        ent_pwd.pack(pady=5)
        ent_pwd.insert(0, "emp123")

        def save_pwd():
            new_p = ent_pwd.get().strip()
            if not new_p:
                messagebox.showerror("Error", "Password cannot be empty.", parent=dialog)
                return

            try:
                conn = database.get_connection()
                cursor = conn.cursor()
                new_hash = utils.hash_password(new_p)
                cursor.execute("UPDATE employees SET password_hash=? WHERE employee_id=?", (new_hash, self.selected_emp_id))
                conn.commit()
                conn.close()

                log_activity("ADMIN", "Admin", "Admin Change Password", f"Admin set new password for {self.selected_emp_id}")
                messagebox.showinfo("Success", f"Password for {self.selected_emp_id} updated successfully.")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update password: {e}", parent=dialog)

        ttk.Button(dialog, text="Save Password", command=save_pwd, style="Primary.TButton").pack(pady=10)

    def delete_employee(self):
        if not self.selected_emp_id:
            messagebox.showwarning("Selection Required", "Please select an employee from the table to delete.")
            return

        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to permanently delete employee '{self.selected_emp_id}'?")
        if confirm:
            try:
                conn = database.get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM employees WHERE employee_id=?", (self.selected_emp_id,))
                conn.commit()
                conn.close()

                log_activity("ADMIN", "Admin", "Delete Employee", f"Deleted employee record {self.selected_emp_id}")
                messagebox.showinfo("Deleted", "Employee record deleted successfully.")
                self.selected_emp_id = None
                self.load_employees()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete record: {e}")

    def load_employees(self):
        for item in self.table.get_children():
            self.table.delete(item)

        search_text = f"%{self.ent_search.get().strip()}%"
        dept_filter = self.combo_filter_dept.get()
        status_filter = self.combo_filter_status.get()

        conn = database.get_connection()
        cursor = conn.cursor()

        query = """
        SELECT employee_id, name, department, designation, phone, joining_date, status 
        FROM employees 
        WHERE (employee_id LIKE ? OR name LIKE ? OR designation LIKE ? OR email LIKE ? OR phone LIKE ?)
        """
        params = [search_text, search_text, search_text, search_text, search_text]

        if dept_filter != "All":
            query += " AND department = ?"
            params.append(dept_filter)
        if status_filter != "All":
            query += " AND status = ?"
            params.append(status_filter)

        query += " ORDER BY employee_id ASC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            self.table.insert("", "end", values=("No records found", "", "", "", "", "", ""))
            return

        for row in rows:
            display_row = (row[0], row[1], row[2], row[3], row[4], utils.db_to_display_date(row[5]), f"● {row[6]}")
            self.table.insert("", "end", values=display_row, tags=(row[6],))

    def reset_search(self):
        self.ent_search.delete(0, tk.END)
        self.combo_filter_dept.set("All")
        self.combo_filter_status.set("All")
        self.load_employees()
