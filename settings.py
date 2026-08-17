import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import database
import utils
from activity_logger import log_activity

class SettingsView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill="both", expand=True)
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Application Settings", font=("Segoe UI", 16, "bold"), foreground="#0f172a").pack(anchor="w", padx=20, pady=(15, 10))

        pwd_frame = ttk.LabelFrame(self, text="Change Admin Password")
        pwd_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(pwd_frame, text="Current Password:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.ent_curr_pass = ttk.Entry(pwd_frame, show="*", width=25)
        self.ent_curr_pass.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(pwd_frame, text="New Password:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.ent_new_pass = ttk.Entry(pwd_frame, show="*", width=25)
        self.ent_new_pass.grid(row=1, column=1, padx=10, pady=5)

        ttk.Button(pwd_frame, text="Update Admin Password", command=self.change_admin_password, style="Primary.TButton").grid(row=2, column=0, columnspan=2, pady=10)

        backup_frame = ttk.LabelFrame(self, text="Database Maintenance")
        backup_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(backup_frame, text="Create a standalone snapshot backup of the current database.").pack(anchor="w", padx=10, pady=5)
        ttk.Button(backup_frame, text="Backup Database Now", command=self.trigger_backup, style="Secondary.TButton").pack(anchor="w", padx=10, pady=5)

    def change_admin_password(self):
        curr = self.ent_curr_pass.get().strip()
        new_p = self.ent_new_pass.get().strip()

        if not curr or not new_p:
            messagebox.showerror("Error", "All password fields are required.")
            return

        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE username='admin'")
        stored_hash = cursor.fetchone()[0]

        if not utils.verify_password(stored_hash, curr):
            messagebox.showerror("Error", "Incorrect current password.")
            conn.close()
            return

        new_hash = utils.hash_password(new_p)
        cursor.execute("UPDATE users SET password_hash=? WHERE username='admin'", (new_hash,))
        conn.commit()
        conn.close()

        log_activity("ADMIN", "Admin", "Change Password", "Admin changed administrative password.")
        messagebox.showinfo("Success", "Admin password updated successfully.")
        self.ent_curr_pass.delete(0, tk.END)
        self.ent_new_pass.delete(0, tk.END)

    def trigger_backup(self):
        try:
            dest = filedialog.askdirectory(title="Select Backup Target Directory")
            backup_file = database.backup_database(dest if dest else None)
            log_activity("ADMIN", "Admin", "Database Backup", f"Database backed up to {backup_file}")
            messagebox.showinfo("Backup Success", f"Database backup saved successfully to:\n{backup_file}")
        except Exception as e:
            messagebox.showerror("Backup Error", f"Failed to create backup: {e}")
