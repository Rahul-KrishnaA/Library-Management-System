import tkinter as tk
from tkinter import messagebox
from main import ScrollableTreeview, MainMenuPage

class LogsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Logs", font=("Arial", 16)).pack(pady=10)

        columns = ("log_id", "library_id", "staff_id", "member_id", "book_id", "activity_type", "description", "timestamp")
        headings = ("Log ID", "Library ID", "Staff ID", "Member ID", "Book ID", "Activity Type", "Description", "Timestamp")

        col_widths = [100, 100, 100, 100, 100, 120, 200, 130]
        self.tree_frame = ScrollableTreeview(self, columns, headings, col_widths=col_widths)
        self.tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree_frame._bind_mousewheel(None)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Refresh", command=self.load_logs).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Back to Menu", command=lambda: controller.show_frame(MainMenuPage)).pack(side="left", padx=5)

        self.load_logs()

    def load_logs(self):
        try:
            conn = self.controller.connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT al.log_id, al.library_id, al.staff_id, al.member_id, al.book_id, at.activity_type, al.description, al.timestamp
                FROM activitylogs al
                JOIN activitytypes at ON al.activity_type_id = at.activity_type_id
                ORDER BY al.timestamp DESC
            """)
            rows = cursor.fetchall()
            cursor.close()
            conn.close()

            self.tree_frame.tree.delete(*self.tree_frame.tree.get_children())
            for row in rows:
                self.tree_frame.tree.insert("", "end", values=row)
        except Exception as err:
            messagebox.showerror("Database Error", f"Error: {err}")
