import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from main import ScrollableTreeview, MainMenuPage

class StaffsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Staffs", font=("Arial", 16)).pack(pady=10)

        columns = ("staff_id", "name", "role", "email", "phone", "hire_date", "salary")
        headings = ("Staff ID", "Name", "Role", "Email", "Phone", "Hire Date", "Salary")

        self.tree_frame = ScrollableTreeview(self, columns, headings)
        self.tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Refresh", command=self.load_staffs).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Add Staff", command=self.add_staff_dialog).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Remove Staff", command=self.remove_staff).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Back to Menu", command=lambda: controller.show_frame(MainMenuPage)).pack(side="left", padx=5)

        self.load_staffs()

    def load_staffs(self):
        try:
            conn = self.controller.connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT staff_id, name, role, email, phone, hire_date, salary FROM librarystaff")
            rows = cursor.fetchall()
            cursor.close()
            conn.close()

            self.tree_frame.tree.delete(*self.tree_frame.tree.get_children())
            for row in rows:
                self.tree_frame.tree.insert("", "end", values=row)
        except Exception as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    def add_staff_dialog(self):
        dialog = AddStaffDialog(self)
        self.wait_window(dialog.top)
        self.load_staffs()

    def remove_staff(self):
        selected = self.tree_frame.tree.selection()
        if not selected:
            messagebox.showwarning("Remove Staff", "Please select a staff to remove.")
            return
        staff_id = self.tree_frame.tree.item(selected[0])['values'][0]

        confirm = messagebox.askyesno("Remove Staff", f"Are you sure you want to remove staff ID {staff_id}?")
        if not confirm:
            return

        try:
            conn = self.controller.connect_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM librarystaff WHERE staff_id=%s", (staff_id,))
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Success", "Staff removed successfully.")
            self.load_staffs()
        except Exception as err:
            messagebox.showerror("Database Error", f"Error: {err}")

class AddStaffDialog:
    def __init__(self, parent):
        top = self.top = tk.Toplevel(parent)
        top.title("Add Staff")

        tk.Label(top, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.name_entry = tk.Entry(top)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(top, text="Role:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.role_entry = tk.Entry(top)
        self.role_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(top, text="Email:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.email_entry = tk.Entry(top)
        self.email_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(top, text="Phone:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.phone_entry = tk.Entry(top)
        self.phone_entry.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(top, text="Hire Date (YYYY-MM-DD):").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.hire_date_entry = tk.Entry(top)
        self.hire_date_entry.grid(row=4, column=1, padx=5, pady=5)

        tk.Label(top, text="Salary:").grid(row=5, column=0, padx=5, pady=5, sticky="e")
        self.salary_entry = tk.Entry(top)
        self.salary_entry.grid(row=5, column=1, padx=5, pady=5)

        tk.Button(top, text="Add", command=self.add_staff).grid(row=6, column=0, columnspan=2, pady=10)

    def add_staff(self):
        name = self.name_entry.get()
        role = self.role_entry.get()
        email = self.email_entry.get()
        phone = self.phone_entry.get()
        hire_date = self.hire_date_entry.get()
        salary = self.salary_entry.get()

        if not (name and role and email and phone and hire_date and salary):
            messagebox.showwarning("Input Error", "Please fill all fields.")
            return

        try:
            salary = float(salary)
            datetime.strptime(hire_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Input Error", "Invalid salary or hire date format.")
            return

        try:
            conn = self.top.master.controller.connect_db()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO librarystaff (name, role, email, phone, hire_date, salary) VALUES (%s, %s, %s, %s, %s, %s)",
                (name, role, email, phone, hire_date, salary)
            )
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Add Staff", "Staff added successfully.")
            self.top.destroy()
        except Exception as err:
            messagebox.showerror("Database Error", f"Error: {err}")
