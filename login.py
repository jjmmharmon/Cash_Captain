import customtkinter as ctk
from tkinter import messagebox, PhotoImage
from db_manager import DatabaseManager
from interface import FinanceManagerUI

ctk.set_appearance_mode("dark")      # dark or light
ctk.set_default_color_theme("blue")  # blue, green, dark-blue

class LoginPage:
    def __init__(self, root):
        self.root = root
        self.root.title("Cash Captain Login")
        self.root.geometry("400x300")
        self.db = DatabaseManager("finance.db")

        # ------------------- Header with Logo -------------------
        icon_image = ctk.CTkImage(
            light_image=PhotoImage(file="cashcaptain.jpg"),
            dark_image=PhotoImage(file="cashcaptain.jpg"),
            size=(50, 50)
        )

        header_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        header_frame.pack(pady=20, padx=20, fill="x")

        # Logo
        self.logo_label = ctk.CTkLabel(header_frame, image=icon_image, text="")
        self.logo_label.pack(side="left")

        # Title
        title_label = ctk.CTkLabel(header_frame, text="Cash Captain", font=("Helvetica", 20))
        title_label.pack(side="left", padx=10)

        # ------------------- Buttons -------------------
        ctk.CTkButton(self.root, text="Login", width=20, command=self.show_login).pack(pady=5)
        ctk.CTkButton(self.root, text="Create User", width=20, command=self.show_create).pack(pady=5)
        ctk.CTkButton(self.root, text="Continue as Guest", width=20, command=self.guest_login).pack(pady=5)

    # -------------------------- LOGIN WINDOW --------------------------
    def show_login(self):
        self.popup = ctk.CTkToplevel(self.root)
        self.popup.title("Login")
        self.popup.geometry("300x200")

        ctk.CTkLabel(self.popup, text="Username").pack(pady=(10,0))
        self.username_entry = ctk.CTkEntry(self.popup)
        self.username_entry.pack(pady=5)

        ctk.CTkLabel(self.popup, text="Password").pack(pady=(10,0))
        self.password_entry = ctk.CTkEntry(self.popup, show="*")
        self.password_entry.pack(pady=5)

        ctk.CTkButton(self.popup, text="Login", command=self.login_user).pack(pady=15)

    def login_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        user_id = self.db.validate_user(username, password)
        if user_id:
            messagebox.showinfo("Success", "Login successful!")
            self.popup.destroy()
            self.start_dashboard(user_id)
        else:
            messagebox.showerror("Error", "Invalid credentials")

    # -------------------------- CREATE USER WINDOW --------------------------
    def show_create(self):
        self.popup = ctk.CTkToplevel(self.root)
        self.popup.title("Create User")
        self.popup.geometry("300x200")

        ctk.CTkLabel(self.popup, text="Username").pack(pady=(10,0))
        self.new_username = ctk.CTkEntry(self.popup)
        self.new_username.pack(pady=5)

        ctk.CTkLabel(self.popup, text="Password").pack(pady=(10,0))
        self.new_password = ctk.CTkEntry(self.popup, show="*")
        self.new_password.pack(pady=5)

        ctk.CTkButton(self.popup, text="Create", command=self.create_user).pack(pady=15)

    def create_user(self):
        username = self.new_username.get()
        password = self.new_password.get()

        if len(password) < 8:
            messagebox.showerror("Error", "Password must be at least 8 characters")
            return

        if self.db.create_user(username, password):
            messagebox.showinfo("Success", "User created!")
            self.popup.destroy()
        else:
            messagebox.showerror("Error", "Username already exists")

    # -------------------------- GUEST LOGIN --------------------------
    def guest_login(self):
        self.start_dashboard(None)

    # -------------------------- START DASHBOARD --------------------------
    def start_dashboard(self, user_id):
        # Clear the root window
        for widget in self.root.winfo_children():
            widget.destroy()
        # Start the dashboard in the same window
        FinanceManagerUI(self.root, self.db, user_id)


if __name__ == "__main__":
    root = ctk.CTk()
    LoginPage(root)
    root.mainloop()
