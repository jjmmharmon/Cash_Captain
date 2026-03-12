import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from db_manager import DatabaseManager
from interface import FinanceManagerUI

# Theme settings
ctk.set_appearance_mode("dark")      # "dark" or "light"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"


class LoginPage:
    def __init__(self, root):
        self.root = root
        self.root.title("Cash Captain Login")
        self.root.geometry("400x300")

        self.db = DatabaseManager("finance.db")

        # Title
        ctk.CTkLabel(root, text="Cash Captain", font=("Helvetica", 24)).pack(pady=30)

        # Buttons
        ctk.CTkButton(root, text="Login", width=200, command=self.show_login).pack(pady=5)
        ctk.CTkButton(root, text="Create User", width=200, command=self.show_create).pack(pady=5)
        ctk.CTkButton(root, text="Continue as Guest", width=200, command=self.guest_login).pack(pady=5)

    # -------------------- LOGIN POPUP --------------------
    def show_login(self):
        self.popup = ctk.CTkToplevel(self.root)
        self.popup.title("Login")
        self.popup.geometry("300x220")
        self.popup.grab_set()

        ctk.CTkLabel(self.popup, text="Username").pack(pady=(15, 0))
        self.username_entry = ctk.CTkEntry(self.popup)
        self.username_entry.pack(pady=5)

        ctk.CTkLabel(self.popup, text="Password").pack(pady=(10, 0))
        self.password_entry = ctk.CTkEntry(self.popup, show="*")
        self.password_entry.pack(pady=5)

        ctk.CTkButton(self.popup, text="Login", command=self.login_user).pack(pady=15)

    # -------------------- CREATE USER POPUP --------------------
    def show_create(self):
        self.popup = ctk.CTkToplevel(self.root)
        self.popup.title("Create User")
        self.popup.geometry("300x220")
        self.popup.grab_set()

        ctk.CTkLabel(self.popup, text="Username").pack(pady=(15, 0))
        self.new_username = ctk.CTkEntry(self.popup)
        self.new_username.pack(pady=5)

        ctk.CTkLabel(self.popup, text="Password").pack(pady=(10, 0))
        self.new_password = ctk.CTkEntry(self.popup, show="*")
        self.new_password.pack(pady=5)

        ctk.CTkButton(self.popup, text="Create", command=self.create_user).pack(pady=15)

    # -------------------- LOGIN FUNCTION --------------------
    def login_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if self.db.validate_user(username, password):
            messagebox.showinfo("Success", "Login successful!")
            self.popup.destroy()
            self.root.withdraw()
            self.start_dashboard(username)
        else:
            messagebox.showerror("Error", "Invalid credentials")

    # -------------------- CREATE USER --------------------
    def create_user(self):
        username = self.new_username.get()
        password = self.new_password.get()

        if self.db.create_user(username, password):
            messagebox.showinfo("Success", "User created!")
            self.popup.destroy()
        else:
            messagebox.showerror("Error", "Username already exists")

    # -------------------- GUEST LOGIN --------------------
    def guest_login(self):
        self.root.withdraw()
        self.start_dashboard()

    # -------------------- START DASHBOARD --------------------
    def start_dashboard(self, user_id=None):
        dash = ctk.CTkToplevel(self.root)
        dash.title("Cash Captain Dashboard")
        dash.geometry("900x600")

        FinanceManagerUI(dash, self.db, user_id)


# -------------------- MAIN PROGRAM --------------------
if __name__ == "__main__":
    root = ctk.CTk()
    LoginPage(root)
    root.mainloop()
