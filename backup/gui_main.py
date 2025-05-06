import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime, timedelta

class LibraryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Library Management System")
        self.geometry("900x650")
        self.resizable(True, True)

        # Define color scheme
        self.bg_color = "#f0f4f8"
        self.accent_color = "#007acc"
        self.button_bg = "#007acc"
        self.button_fg = "#ffffff"
        self.label_fg = "#003366"
        self.font_family = "Segoe UI"

        self.configure(bg=self.bg_color)

        self.db_config = {
            "host": "localhost",
            "user": "root",
            "password": "3583",
            "database": "lib_management"
        }
        self.admin_id = None

        self.container = tk.Frame(self, bg=self.bg_color)
        self.container.pack(fill="both", expand=True)

        self.frames = {}
        for F in (LoginPage, MainMenuPage, BooksPage, MembersPage, FinesPage, StaffsPage, LogsPage, ReservationsPage,
                  IssueBookPage, ReturnBookPage, AddReservationPage, CancelReservationPage):
            frame = F(parent=self.container, controller=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(LoginPage)
        
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def connect_db(self):
        return mysql.connector.connect(**self.db_config)

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=controller.bg_color)
        self.controller = controller

        tk.Label(self, text="Admin Login", font=(controller.font_family, 24, "bold"), fg=controller.accent_color, bg=controller.bg_color).pack(pady=20)

        tk.Label(self, text="Username:", font=(controller.font_family, 12), fg=controller.label_fg, bg=controller.bg_color).pack(pady=5)
        self.username_entry = tk.Entry(self, font=(controller.font_family, 12))
        self.username_entry.pack(ipady=5, ipadx=5)

        tk.Label(self, text="Password:", font=(controller.font_family, 12), fg=controller.label_fg, bg=controller.bg_color).pack(pady=5)
        self.password_entry = tk.Entry(self, show="*", font=(controller.font_family, 12))
        self.password_entry.pack(ipady=5, ipadx=5)

        login_btn = tk.Button(self, text="Login", command=self.login, bg=controller.button_bg, fg=controller.button_fg,
                              font=(controller.font_family, 12, "bold"), activebackground="#005a9e", activeforeground="#ffffff", relief="flat")
        login_btn.pack(pady=20)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        try:
            conn = self.controller.connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT admin_id FROM admin WHERE name=%s AND password=%s", (username, password))
            result = cursor.fetchone()
            cursor.close()
            conn.close()

            if result:
                self.controller.admin_id = result[0]
                messagebox.showinfo("Login", "Login successful.")
                self.controller.show_frame(MainMenuPage)
            else:
                messagebox.showerror("Login Failed", "Wrong username or password.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

class MainMenuPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=controller.bg_color)
        self.controller = controller

        tk.Label(self, text="Main Menu", font=(controller.font_family, 24, "bold"), fg=controller.accent_color, bg=controller.bg_color).pack(pady=20)

        buttons = [
            ("View Books", BooksPage),
            ("Issue Book", IssueBookPage),
            ("Return Book", ReturnBookPage),
            ("View Members", MembersPage),
            ("View Fines", FinesPage),
            ("View Staffs", StaffsPage),
            ("View Logs", LogsPage),
            ("View Reservations", ReservationsPage),
            ("Add Reservation", AddReservationPage),
            ("Cancel Reservation", CancelReservationPage),
            ("Exit", self.exit_app)
        ]

        for (text, page) in buttons:
            action = page if callable(page) else page
            btn = tk.Button(self, text=text, width=20, bg=controller.button_bg, fg=controller.button_fg,
                            font=(controller.font_family, 12, "bold"), relief="flat",
                            activebackground="#005a9e", activeforeground="#ffffff",
                            command=lambda p=page: self.open_page(p))
            btn.pack(pady=5)

    def open_page(self, page):
        if page == self.exit_app:
            self.exit_app()
        else:
            self.controller.show_frame(page)

    def exit_app(self):
        self.controller.destroy()

class ScrollableTreeview(ttk.Frame):
    def __init__(self, parent, columns, headings):
        super().__init__(parent)

        style = ttk.Style()
        style.theme_use('default')
        style.configure("Treeview",
                        background="#f0f4f8",
                        foreground="#003366",
                        rowheight=25,
                        fieldbackground="#f0f4f8",
                        font=("Segoe UI", 10))
        style.map('Treeview', background=[('selected', '#007acc')], foreground=[('selected', 'white')])

        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col, head in zip(columns, headings):
            self.tree.heading(col, text=head)
            self.tree.column(col, width=100, anchor="center")

        self.vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.hsb = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        self.vsb.grid(row=0, column=1, sticky="ns")
        self.hsb.grid(row=1, column=0, sticky="ew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Bind mouse wheel for vertical and horizontal scrolling
        self.tree.bind("<Enter>", self._bind_mousewheel)
        self.tree.bind("<Leave>", self._unbind_mousewheel)

    def _bind_mousewheel(self, event):
        # Bind mouse wheel events for vertical and horizontal scrolling
        self.tree.bind_all("<MouseWheel>", self._on_mousewheel)
        self.tree.bind_all("<Shift-MouseWheel>", self._on_shift_mousewheel)
        # For Linux systems using Button-4 and Button-5 for scroll
        self.tree.bind_all("<Button-4>", self._on_mousewheel_linux)
        self.tree.bind_all("<Button-5>", self._on_mousewheel_linux)
        self.tree.bind_all("<Shift-Button-4>", self._on_shift_mousewheel_linux)
        self.tree.bind_all("<Shift-Button-5>", self._on_shift_mousewheel_linux)

    def _unbind_mousewheel(self, event):
        self.tree.unbind_all("<MouseWheel>")
        self.tree.unbind_all("<Shift-MouseWheel>")
        self.tree.unbind_all("<Button-4>")
        self.tree.unbind_all("<Button-5>")
        self.tree.unbind_all("<Shift-Button-4>")
        self.tree.unbind_all("<Shift-Button-5>")

    def _on_mousewheel(self, event):
        # Vertical scroll for Windows and MacOS
        if event.delta:
            self.tree.yview_scroll(int(-1*(event.delta/120)), "units")

    def _on_shift_mousewheel(self, event):
        # Horizontal scroll when shift is pressed for Windows and MacOS
        if event.delta:
            self.tree.xview_scroll(int(-1*(event.delta/120)), "units")

    def _on_mousewheel_linux(self, event):
        # Vertical scroll for Linux (Button-4 scroll up, Button-5 scroll down)
        if event.num == 4:
            self.tree.yview_scroll(-1, "units")
        elif event.num == 5:
            self.tree.yview_scroll(1, "units")

    def _on_shift_mousewheel_linux(self, event):
        # Horizontal scroll for Linux with shift + Button-4/Button-5
        if event.num == 4:
            self.tree.xview_scroll(-1, "units")
        elif event.num == 5:
            self.tree.xview_scroll(1, "units")

class BooksPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Books", font=("Arial", 16)).pack(pady=10)

        columns = ("book_id", "library_id", "title", "genre", "isbn", "published_year", "copies_available")
        headings = ("Book ID", "Library ID", "Title", "Genre", "ISBN", "Year", "Copies")

        self.tree_frame = ScrollableTreeview(self, columns, headings)
        self.tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Refresh", command=self.load_books).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Add Book", command=self.add_book_dialog).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Delete Book", command=self.delete_book_dialog).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Back to Menu", command=lambda: controller.show_frame(MainMenuPage)).pack(side="left", padx=5)

        self.load_books()

    def load_books(self):
        try:
            conn = self.controller.connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT book_id, library_id, title, genre, isbn, published_year, copies_available FROM books")
            rows = cursor.fetchall()
            cursor.close()
            conn.close()

            self.tree_frame.tree.delete(*self.tree_frame.tree.get_children())
            for row in rows:
                self.tree_frame.tree.insert("", "end", values=row)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    def add_book_dialog(self):
        dialog = AddBookDialog(self)
        self.wait_window(dialog.top)
        self.load_books()

    def delete_book_dialog(self):
        selected = self.tree_frame.tree.selection()
        if not selected:
            messagebox.showwarning("Delete Book", "Please select a book to delete.")
            return
        book_id = self.tree_frame.tree.item(selected[0])['values'][0]
        confirm = messagebox.askyesno("Delete Book", f"Are you sure you want to delete book ID {book_id}?")
        if confirm:
            try:
                conn = self.controller.connect_db()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM books WHERE book_id=%s", (book_id,))
                conn.commit()
                cursor.close()
                conn.close()
                messagebox.showinfo("Delete Book", "Book deleted.")
                self.load_books()
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error: {err}")

class AddBookDialog:
    def __init__(self, parent):
        top = self.top = tk.Toplevel(parent)
        top.title("Add Book")

        tk.Label(top, text="Title:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.title_entry = tk.Entry(top)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(top, text="Genre:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.genre_entry = tk.Entry(top)
        self.genre_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(top, text="ISBN:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.isbn_entry = tk.Entry(top)
        self.isbn_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(top, text="Published Year:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.year_entry = tk.Entry(top)
        self.year_entry.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(top, text="Copies Available:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.copies_entry = tk.Entry(top)
        self.copies_entry.grid(row=4, column=1, padx=5, pady=5)

        tk.Label(top, text="Library ID:").grid(row=5, column=0, padx=5, pady=5, sticky="e")
        self.library_id_entry = tk.Entry(top)
        self.library_id_entry.grid(row=5, column=1, padx=5, pady=5)

        tk.Button(top, text="Add", command=self.add_book).grid(row=6, column=0, columnspan=2, pady=10)

    def add_book(self):
        title = self.title_entry.get()
        genre = self.genre_entry.get()
        isbn = self.isbn_entry.get()
        year = self.year_entry.get()
        copies = self.copies_entry.get()
        library_id = self.library_id_entry.get()

        if not (title and genre and isbn and year and copies and library_id):
            messagebox.showwarning("Input Error", "Please fill all fields.")
            return

        try:
            year = int(year)
            copies = int(copies)
            library_id = int(library_id)
        except ValueError:
            messagebox.showwarning("Input Error", "Year, Copies, and Library ID must be integers.")
            return

        try:
            conn = self.top.master.controller.connect_db()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO books (library_id, title, genre, isbn, published_year, copies_available) VALUES (%s, %s, %s, %s, %s, %s)",
                (library_id, title, genre, isbn, year, copies)
            )
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Add Book", "Book added successfully.")
            self.top.destroy()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

# Similar pages for Members, Fines, Staffs, Logs, Reservations can be implemented similarly.
# For brevity, I will implement MembersPage as an example.

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
        except mysql.connector.Error as err:
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
            except mysql.connector.Error as err:
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
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

# Placeholder classes for other pages to be implemented similarly
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
        except mysql.connector.Error as err:
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
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

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
        except mysql.connector.Error as err:
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
        except mysql.connector.Error as err:
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
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

class LogsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Logs", font=("Arial", 16)).pack(pady=10)

        columns = ("log_id", "library_id", "staff_id", "member_id", "book_id", "activity_type", "description", "timestamp")
        headings = ("Log ID", "Library ID", "Staff ID", "Member ID", "Book ID", "Activity Type", "Description", "Timestamp")

        self.tree_frame = ScrollableTreeview(self, columns, headings)
        self.tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

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
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

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
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

# Placeholder pages for the new menu options

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

        except mysql.connector.Error as err:
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

        except mysql.connector.Error as err:
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

        except mysql.connector.Error as err:
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
        except mysql.connector.Error as err:
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

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

if __name__ == "__main__":
    app = LibraryApp()
    app.mainloop()


