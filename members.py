import tkinter as tk
from tkinter import messagebox
from main import ScrollableTreeview, MainMenuPage

class MembersPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Members", font=("Arial", 16)).pack(pady=10)

        columns = ("member_id", "library_id", "name", "email", "phone", "membership_type")
        headings = ("Member ID", "Library ID", "Name", "Email", "Phone", "Membership Type")

        self.tree_frame = ScrollableTreeview(self, columns, headings)
        self.tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Refresh", command=self.load_members).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Add Member", command=self.add_member_dialog).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Remove Member", command=self.remove_member_dialog).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Back to Menu", command=lambda: controller.show_frame(MainMenuPage)).pack(side="left", padx=5)

        self.load_members()

    def load_members(self):
        try:
            conn = self.controller.connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT member_id, library_id, name, email, phone, membership_type FROM members")
            rows = cursor.fetchall()
            cursor.close()
            conn.close()

            self.tree_frame.tree.delete(*self.tree_frame.tree.get_children())
            for row in rows:
                self.tree_frame.tree.insert("", "end", values=row)
        except Exception as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    def add_member_dialog(self):
        dialog = AddMemberDialog(self)
        self.wait_window(dialog.top)
        self.load_members()

    def remove_member_dialog(self):
        selected = self.tree_frame.tree.selection()
        if not selected:
            messagebox.showwarning("Remove Member", "Please select a member to remove.")
            return
        member_id = self.tree_frame.tree.item(selected[0])['values'][0]
        confirm = messagebox.askyesno("Remove Member", f"Are you sure you want to remove member ID {member_id}?")
        if confirm:
            try:
                conn = self.controller.connect_db()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM members WHERE member_id=%s", (member_id,))
                conn.commit()
                cursor.close()
                conn.close()
                messagebox.showinfo("Remove Member", "Member removed.")
                self.load_members()
            except Exception as err:
                messagebox.showerror("Database Error", f"Error: {err}")

class AddMemberDialog:
    def __init__(self, parent):
        top = self.top = tk.Toplevel(parent)
        top.title("Add Member")

        tk.Label(top, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.name_entry = tk.Entry(top)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(top, text="Email:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.email_entry = tk.Entry(top)
        self.email_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(top, text="Phone:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.phone_entry = tk.Entry(top)
        self.phone_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(top, text="Membership Type:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.membership_entry = tk.Entry(top)
        self.membership_entry.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(top, text="Library ID:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.library_id_entry = tk.Entry(top)
        self.library_id_entry.grid(row=4, column=1, padx=5, pady=5)

        tk.Button(top, text="Add", command=self.add_member).grid(row=5, column=0, columnspan=2, pady=10)

    def add_member(self):
        name = self.name_entry.get()
        email = self.email_entry.get()
        phone = self.phone_entry.get()
        membership_type = self.membership_entry.get()
        library_id = self.library_id_entry.get()

        if not (name and email and phone and membership_type and library_id):
            messagebox.showwarning("Input Error", "Please fill all fields.")
            return

        try:
            library_id = int(library_id)
        except ValueError:
            messagebox.showwarning("Input Error", "Library ID must be an integer.")
            return

        try:
            conn = self.top.master.controller.connect_db()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO members (library_id, name, email, phone, membership_type) VALUES (%s, %s, %s, %s, %s)",
                (library_id, name, email, phone, membership_type)
            )
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Add Member", "Member added successfully.")
            self.top.destroy()
        except Exception as err:
            messagebox.showerror("Database Error", f"Error: {err}")
