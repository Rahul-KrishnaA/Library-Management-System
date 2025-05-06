import tkinter as tk
from tkinter import messagebox
from main import ScrollableTreeview, MainMenuPage

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
        except Exception as err:
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
            except Exception as err:
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
        except Exception as err:
            messagebox.showerror("Database Error", f"Error: {err}")
