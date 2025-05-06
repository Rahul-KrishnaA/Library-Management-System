import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime

class LibraryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Library Management System")
        self.geometry("1000x650")
        self.resizable(True, True)

        self.update_idletasks()
        width = 1000
        height = 650
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

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

        from books import BooksPage
        from members import MembersPage
        from fines import FinesPage
        from staffs import StaffsPage
        from logs import LogsPage
        from reservations import ReservationsPage, AddReservationPage, CancelReservationPage
        from issue_return import IssueBookPage, ReturnBookPage
        from main import LoginPage, MainMenuPage, ScrollableTreeview  # will be defined below

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
            ("View Books", "BooksPage"),
            ("Issue Book", "IssueBookPage"),
            ("Return Book", "ReturnBookPage"),
            ("View Members", "MembersPage"),
            ("View Fines", "FinesPage"),
            ("View Staffs", "StaffsPage"),
            ("View Logs", "LogsPage"),
            ("View Reservations", "ReservationsPage"),
            ("Add Reservation", "AddReservationPage"),
            ("Cancel Reservation", "CancelReservationPage"),
            ("Exit", self.exit_app)
        ]

        for (text, page) in buttons:
            if callable(page):
                action = page
            else:
                action = lambda p=page: self.open_page(p)
            btn = tk.Button(self, text=text, width=20, bg=controller.button_bg, fg=controller.button_fg,
                            font=(controller.font_family, 12, "bold"), relief="flat",
                            activebackground="#005a9e", activeforeground="#ffffff",
                            command=action)
            btn.pack(pady=5)

    def open_page(self, page_name):
        # Map string page names to actual classes
        page_class = None
        for cls in self.controller.frames:
            if cls.__name__ == page_name:
                page_class = cls
                break
        if page_class:
            self.controller.show_frame(page_class)

    def exit_app(self):
        self.controller.destroy()

class ScrollableTreeview(ttk.Frame):
    def __init__(self, parent, columns, headings, col_widths=None):
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
        for idx, (col, head) in enumerate(zip(columns, headings)):
            self.tree.heading(col, text=head)
            width = 100
            if col_widths and idx < len(col_widths):
                width = col_widths[idx]
            self.tree.column(col, width=width, anchor="center")

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
        # Bind mouse wheel events for vertical and horizontal scrolling directly to the tree widget
        self.tree.bind("<MouseWheel>", self._on_mousewheel)
        self.tree.bind("<Shift-MouseWheel>", self._on_shift_mousewheel)
        # For Linux systems using Button-4 and Button-5 for scroll
        self.tree.bind("<Button-4>", self._on_mousewheel_linux)
        self.tree.bind("<Button-5>", self._on_mousewheel_linux)
        self.tree.bind("<Shift-Button-4>", self._on_shift_mousewheel_linux)
        self.tree.bind("<Shift-Button-5>", self._on_shift_mousewheel_linux)

    def _unbind_mousewheel(self, event):
        self.tree.unbind("<MouseWheel>")
        self.tree.unbind("<Shift-MouseWheel>")
        self.tree.unbind("<Button-4>")
        self.tree.unbind("<Button-5>")
        self.tree.unbind("<Shift-Button-4>")
        self.tree.unbind("<Shift-Button-5>")

    def _on_mousewheel(self, event):
        # Vertical scroll for Windows and MacOS
        if event.delta:
            self.tree.yview_scroll(int(-1*(event.delta/120)), "units")
        return "break"

    def _on_shift_mousewheel(self, event):
        # Horizontal scroll when shift is pressed for Windows and MacOS
        if event.delta:
            self.tree.xview_scroll(int(-1*(event.delta/120)), "units")
        return "break"

    def _on_mousewheel_linux(self, event):
        # Vertical scroll for Linux (Button-4 scroll up, Button-5 scroll down)
        if event.num == 4:
            self.tree.yview_scroll(-1, "units")
        elif event.num == 5:
            self.tree.yview_scroll(1, "units")
        return "break"

    def _on_shift_mousewheel_linux(self, event):
        # Horizontal scroll for Linux with shift + Button-4/Button-5
        if event.num == 4:
            self.tree.xview_scroll(-1, "units")
        elif event.num == 5:
            self.tree.xview_scroll(1, "units")
        return "break"

if __name__ == "__main__":
    app = LibraryApp()
    app.mainloop()
