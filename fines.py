import tkinter as tk
from tkinter import messagebox
from main import ScrollableTreeview, MainMenuPage

class FinesPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Fines", font=("Arial", 16)).pack(pady=10)

        columns = ("fine_id", "member_id", "amount", "paid_status", "due_date")
        headings = ("Fine ID", "Member ID", "Amount", "Paid Status", "Due Date")

        self.tree_frame = ScrollableTreeview(self, columns, headings)
        self.tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Refresh", command=self.load_fines).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Mark as Paid", command=self.mark_as_paid).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Back to Menu", command=lambda: controller.show_frame(MainMenuPage)).pack(side="left", padx=5)

        self.load_fines()

    def load_fines(self):
        try:
            conn = self.controller.connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT f.fine_id, f.member_id, fa.amount, f.status, f.payment_date
                FROM fines f
                JOIN fine_amounts fa ON f.fine_id = fa.fine_id
            """)
            rows = cursor.fetchall()
            cursor.close()
            conn.close()

            self.tree_frame.tree.delete(*self.tree_frame.tree.get_children())
            for row in rows:
                self.tree_frame.tree.insert("", "end", values=row)
        except Exception as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    def mark_as_paid(self):
        selected = self.tree_frame.tree.selection()
        if not selected:
            messagebox.showwarning("Mark as Paid", "Please select a fine to mark as paid.")
            return
        fine_id = self.tree_frame.tree.item(selected[0])['values'][0]

        confirm = messagebox.askyesno("Mark as Paid", f"Are you sure you want to mark fine ID {fine_id} as paid?")
        if not confirm:
            return

        try:
            conn = self.controller.connect_db()
            cursor = conn.cursor()
            cursor.execute("UPDATE fines SET paid_status = 'Paid' WHERE fine_id=%s", (fine_id,))
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Success", "Fine marked as paid.")
            self.load_fines()
        except Exception as err:
            messagebox.showerror("Database Error", f"Error: {err}")
