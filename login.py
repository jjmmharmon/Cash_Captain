import tkinter as tk
from tkinter import messagebox
from db_manager import DatabaseManager
from interface import FinanceManagerUI

class LoginPage:
    def __init__(self, root):
        self.root = root
        self.root.title("Cash Captain Login")
        self.root.geometry("400x300")
        self.db = DatabaseManager("finance.db")

        tk.Label(root, text="Cash Captain", font=("Helvetica", 20)).pack(pady=20)

        tk.Button(root, text="Login", width=20, command=self.show_login).pack(pady=5)
        tk.Button(root, text="Create User", width=20, command=self.show_create).pack(pady=5)
        tk.Button(root, text="Continue as Guest", width=20, command=self.guest_login).pack(pady=5)

    def show_login(self):
        self.popup = tk.Toplevel(self.root)
        self.popup.title("Login")
        self.popup.geometry("300x200")

        tk.Label(self.popup, text="Username").pack()
        self.username_entry = tk.Entry(self.popup)
        self.username_entry.pack()

        tk.Label(self.popup, text="Password").pack()
        self.password_entry = tk.Entry(self.popup, show="*")
        self.password_entry.pack()

        tk.Button(self.popup, text="Login", command=self.login_user).pack(pady=10)

    def show_create(self):
        self.popup = tk.Toplevel(self.root)
        self.popup.title("Create User")
        self.popup.geometry("300x200")

        tk.Label(self.popup, text="Username").pack()
        self.new_username = tk.Entry(self.popup)
        self.new_username.pack()

        tk.Label(self.popup, text="Password").pack()
        self.new_password = tk.Entry(self.popup, show="*")
        self.new_password.pack()

        tk.Button(self.popup, text="Create", command=self.create_user).pack(pady=10)

    def login_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if self.db.validate_user(username, password):
            messagebox.showinfo("Success", "Login successful!")
            self.popup.destroy()
            self.root.withdraw()
            self.start_dashboard()
        else:
            messagebox.showerror("Error", "Invalid credentials")

    def create_user(self):
        username = self.new_username.get()
        password = self.new_password.get()
        if self.db.create_user(username, password):
            messagebox.showinfo("Success", "User created!")
            self.popup.destroy()
        else:
            messagebox.showerror("Error", "Username already exists")

    def guest_login(self):
        self.root.withdraw()
        self.start_dashboard()

    def start_dashboard(self):
        dash = tk.Toplevel(self.root)
        db = self.db
        FinanceManagerUI(dash, db)

if __name__ == "__main__":
    root = tk.Tk()
    LoginPage(root)
    root.mainloop()
