import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from main import ScrollableTreeview, MainMenuPage

class ReservationsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Reservations", font=("Arial", 16)).pack(pady=10)

        columns = ("reservation_id", "book_id", "member_id", "reservation_date")
        headings = ("Reservation ID", "Book ID", "Member ID", "Reservation Date")

        self.tree_frame = ScrollableTreeview(self, columns, headings)
        self.tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Refresh", command=self.load_reservations).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Back to Menu", command=lambda: controller.show_frame(MainMenuPage)).pack(side="left", padx=5)

        self.load_reservations()

    def load_reservations(self):
        try:
            conn = self.controller.connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT reservation_id, book_id, member_id, reservation_date FROM reservations")
            rows = cursor.fetchall()
            cursor.close()
            conn.close()

            self.tree_frame.tree.delete(*self.tree_frame.tree.get_children())
            for row in rows:
                self.tree_frame.tree.insert("", "end", values=row)
        except Exception as err:
            messagebox.showerror("Database Error", f"Error: {err}")

class AddReservationPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Add Reservation", font=("Arial", 16)).pack(pady=10)

        form_frame = tk.Frame(self)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Book ID:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.book_id_entry = tk.Entry(form_frame)
        self.book_id_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Member ID:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.member_id_entry = tk.Entry(form_frame)
        self.member_id_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Reservation Date (YYYY-MM-DD):").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.reservation_date_entry = tk.Entry(form_frame)
        self.reservation_date_entry.grid(row=2, column=1, padx=5, pady=5)
        self.reservation_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        tk.Button(form_frame, text="Add Reservation", command=self.add_reservation).grid(row=3, column=0, columnspan=2, pady=10)

        tk.Button(self, text="Back to Menu", command=lambda: controller.show_frame(MainMenuPage)).pack(pady=10)

    def add_reservation(self):
        book_id = self.book_id_entry.get()
        member_id = self.member_id_entry.get()
        reservation_date = self.reservation_date_entry.get()

        if not (book_id and member_id and reservation_date):
            messagebox.showwarning("Input Error", "Please fill all fields.")
            return

        try:
            book_id = int(book_id)
            member_id = int(member_id)
            datetime.strptime(reservation_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Input Error", "Invalid input format.")
            return

        try:
            conn = self.controller.connect_db()
            cursor = conn.cursor()

            # Check if book exists
            cursor.execute("SELECT book_id FROM books WHERE book_id=%s", (book_id,))
            if not cursor.fetchone():
                messagebox.showerror("Error", "Book ID not found.")
                cursor.close()
                conn.close()
                return

            # Check if member exists
            cursor.execute("SELECT member_id FROM members WHERE member_id=%s", (member_id,))
            if not cursor.fetchone():
                messagebox.showerror("Error", "Member ID not found.")
                cursor.close()
                conn.close()
                return

            # Insert reservation
            cursor.execute(
                "INSERT INTO reservations (book_id, member_id, reservation_date) VALUES (%s, %s, %s)",
                (book_id, member_id, reservation_date)
            )

            conn.commit()
            cursor.close()
            conn.close()

            messagebox.showinfo("Success", "Reservation added successfully.")
            self.book_id_entry.delete(0, tk.END)
            self.member_id_entry.delete(0, tk.END)

        except Exception as err:
            messagebox.showerror("Database Error", f"Error: {err}")

class CancelReservationPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Cancel Reservation", font=("Arial", 16)).pack(pady=10)

        columns = ("reservation_id", "book_id", "member_id", "reservation_date")
        headings = ("Reservation ID", "Book ID", "Member ID", "Reservation Date")

        self.tree_frame = ScrollableTreeview(self, columns, headings)
        self.tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Refresh", command=self.load_reservations).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Cancel Reservation", command=self.cancel_reservation).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Back to Menu", command=lambda: controller.show_frame(MainMenuPage)).pack(side="left", padx=5)

        self.load_reservations()

    def load_reservations(self):
        try:
            conn = self.controller.connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT reservation_id, book_id, member_id, reservation_date FROM reservations")
            rows = cursor.fetchall()
            cursor.close()
            conn.close()

            self.tree_frame.tree.delete(*self.tree_frame.tree.get_children())
            for row in rows:
                self.tree_frame.tree.insert("", "end", values=row)
        except Exception as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    def cancel_reservation(self):
        selected = self.tree_frame.tree.selection()
        if not selected:
            messagebox.showwarning("Cancel Reservation", "Please select a reservation to cancel.")
            return
        reservation_id = self.tree_frame.tree.item(selected[0])['values'][0]

        confirm = messagebox.askyesno("Cancel Reservation", f"Are you sure you want to cancel reservation ID {reservation_id}?")
        if not confirm:
            return

        try:
            conn = self.controller.connect_db()
            cursor = conn.cursor()

            cursor.execute("DELETE FROM reservations WHERE reservation_id=%s", (reservation_id,))

            conn.commit()
            cursor.close()
            conn.close()

            messagebox.showinfo("Success", "Reservation cancelled successfully.")
            self.load_reservations()

        except Exception as err:
            messagebox.showerror("Database Error", f"Error: {err}")
