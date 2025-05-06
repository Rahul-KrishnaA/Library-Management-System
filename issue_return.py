import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from main import MainMenuPage

class IssueBookPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Issue Book", font=("Arial", 16)).pack(pady=10)

        form_frame = tk.Frame(self)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Select Book ID:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.book_id_entry = tk.Entry(form_frame)
        self.book_id_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Select Member ID:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.member_id_entry = tk.Entry(form_frame)
        self.member_id_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(form_frame, text="Issue Book", command=self.issue_book).grid(row=2, column=0, columnspan=2, pady=10)

        tk.Button(self, text="Back to Menu", command=lambda: controller.show_frame(MainMenuPage)).pack(pady=10)

    def issue_book(self):
        book_id = self.book_id_entry.get()
        member_id = self.member_id_entry.get()

        if not (book_id and member_id):
            messagebox.showwarning("Input Error", "Please enter both Book ID and Member ID.")
            return

        try:
            book_id = int(book_id)
            member_id = int(member_id)
        except ValueError:
            messagebox.showwarning("Input Error", "Book ID and Member ID must be integers.")
            return

        try:
            conn = self.controller.connect_db()
            cursor = conn.cursor()

            # Check if book has available copies
            cursor.execute("SELECT copies_available FROM books WHERE book_id=%s", (book_id,))
            result = cursor.fetchone()
            if not result:
                messagebox.showerror("Error", "Book ID not found.")
                cursor.close()
                conn.close()
                return
            copies_available = result[0]
            if copies_available <= 0:
                messagebox.showerror("Error", "No copies available for this book.")
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

            # Insert into issued_books table
            issue_date = datetime.now().strftime("%Y-%m-%d")
            cursor.execute(
                "INSERT INTO issued_books (book_id, member_id, issue_date) VALUES (%s, %s, %s)",
                (book_id, member_id, issue_date)
            )

            # Decrement copies_available
            cursor.execute(
                "UPDATE books SET copies_available = copies_available - 1 WHERE book_id=%s",
                (book_id,)
            )

            conn.commit()
            cursor.close()
            conn.close()

            messagebox.showinfo("Success", "Book issued successfully.")
            self.book_id_entry.delete(0, tk.END)
            self.member_id_entry.delete(0, tk.END)

        except Exception as err:
            messagebox.showerror("Database Error", f"Error: {err}")

class ReturnBookPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Return Book", font=("Arial", 16)).pack(pady=10)

        form_frame = tk.Frame(self)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Issue ID:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.issue_id_entry = tk.Entry(form_frame)
        self.issue_id_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Book ID:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.book_id_entry = tk.Entry(form_frame)
        self.book_id_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Member ID:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.member_id_entry = tk.Entry(form_frame)
        self.member_id_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Button(form_frame, text="Return Book", command=self.return_book).grid(row=3, column=0, columnspan=2, pady=10)

        tk.Button(self, text="Back to Menu", command=lambda: controller.show_frame(MainMenuPage)).pack(pady=10)

    def return_book(self):
        issue_id = self.issue_id_entry.get()
        book_id = self.book_id_entry.get()
        member_id = self.member_id_entry.get()

        if not (issue_id and book_id and member_id):
            messagebox.showwarning("Input Error", "Please fill all fields.")
            return

        try:
            issue_id = int(issue_id)
            book_id = int(book_id)
            member_id = int(member_id)
        except ValueError:
            messagebox.showwarning("Input Error", "Issue ID, Book ID, and Member ID must be integers.")
            return

        try:
            conn = self.controller.connect_db()
            cursor = conn.cursor()

            # Check if issue record exists
            cursor.execute("SELECT * FROM issued_books WHERE issue_id=%s AND book_id=%s AND member_id=%s",
                           (issue_id, book_id, member_id))
            if not cursor.fetchone():
                messagebox.showerror("Error", "No matching issued book record found.")
                cursor.close()
                conn.close()
                return

            # Delete from issued_books
            cursor.execute("DELETE FROM issued_books WHERE issue_id=%s", (issue_id,))

            # Increment copies_available
            cursor.execute(
                "UPDATE books SET copies_available = copies_available + 1 WHERE book_id=%s",
                (book_id,)
            )

            # Insert into logs table
            log_message = f"Book returned: Book ID {book_id}, Member ID {member_id}, Issue ID {issue_id}"
            cursor.execute(
                "INSERT INTO logs (log_message, log_date) VALUES (%s, %s)",
                (log_message, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )

            conn.commit()
            cursor.close()
            conn.close()

            messagebox.showinfo("Success", "Book returned successfully.")
            self.issue_id_entry.delete(0, tk.END)
            self.book_id_entry.delete(0, tk.END)
            self.member_id_entry.delete(0, tk.END)

        except Exception as err:
            messagebox.showerror("Database Error", f"Error: {err}")
