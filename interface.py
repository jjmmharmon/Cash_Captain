import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import matplotlib.pyplot as plt
import csv


class FinanceManagerUI:
    def __init__(self, root, db, user_id):
        self.root = root
        self.db = db
        self.user_id = user_id

        # Categories must be defined first
        self.default_categories = [
            "Groceries",
            "Gas",
            "Rent",
            "Entertainment",
            "Savings",
            "Misc",
        ]
        self.next_guest_tid = 1  # Unique ID counter for guest transactions
        self.custom_categories = []
        self.budgets = {cat: 0 for cat in self.default_categories}
        self.guest_budgets = {cat: 0 for cat in self.default_categories}
        self.guest_transactions = []  # Guest transactions
        self.follow_budget = True

        ctk.set_default_color_theme("blue")

        self.create_tabs()
        self.setup_dashboard_tab()
        self.setup_transactions_tab()
        self.setup_budgets_tab()
        self.setup_reports_tab()

        # 🔐 Load transactions if logged in
        self.load_transactions()

    # ---------------- TABS ----------------
    def create_tabs(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both")

        self.dashboard_tab = ctk.CTkFrame(self.notebook)
        self.transactions_tab = ctk.CTkFrame(self.notebook)
        self.budgets_tab = ctk.CTkFrame(self.notebook)
        self.reports_tab = ctk.CTkFrame(self.notebook)

        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.notebook.add(self.transactions_tab, text="Transactions")
        self.notebook.add(self.budgets_tab, text="Budgets")
        self.notebook.add(self.reports_tab, text="Reports")

    # ---------------- DASHBOARD ----------------
    def setup_dashboard_tab(self):
        center_frame = ctk.CTkFrame(self.dashboard_tab)
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            center_frame, text="Cash Captain", font=("Cambria", 60), text_color="blue"
        ).pack(pady=10)

        self.balance_label = ctk.CTkLabel(
            center_frame,
            text="Balance: $0.00",
            font=("Calibri", 40),
            text_color="green",
        )
        self.balance_label.pack(pady=8)

        ctk.CTkButton(
            center_frame,
            text="Refresh",
            command=self.load_transactions,
            font=("Calibri", 20),
        ).pack(pady=8)

    # ---------------- CATEGORIES Getter ----------------
    def get_all_categories(self):
        return self.default_categories + self.custom_categories

    # ---------------- ADD CUSTOM CATEGORY ----------------
    def add_custom_category(self, cat):
        self.custom_categories.append(cat)

        # Add to budget data
        self.budgets[cat] = 0
        self.guest_budgets[cat] = 0

        # ✅ Add to Budget Tab
        self.add_custom_category_to_budget_tab(cat)

        # ✅ Add to right-side overview
        self.add_custom_category_to_overview(cat)

        # ✅ Update transaction dropdown
        if hasattr(self, "category_dropdown"):
            self.category_dropdown["values"] = self.get_all_categories()

        # ✅ Update filter dropdown
        if hasattr(self, "filter_dropdown"):
            self.filter_dropdown["values"] = ["All"] + self.get_all_categories()

        if hasattr(self, "budget_labels"):
            self.update_budget()

    # ---------------- TRANSACTIONS ----------------
    def setup_transactions_tab(self):
        main = ctk.CTkFrame(self.transactions_tab)
        main.pack(fill="both", expand=True, padx=10, pady=10)

        # ---------------- Top Income Entry ----------------
        top_frame = ctk.CTkFrame(main, fg_color="#e6f2ff")
        top_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(
            top_frame, text="Income:", text_color="#003366", font=("Arial", 14)
        ).pack(side="left", padx=5)
        self.income_entry = ctk.CTkEntry(top_frame, placeholder_text="Enter amount")
        self.income_entry.pack(side="left", padx=5)
        ctk.CTkButton(
            top_frame,
            text="Add Income",
            text_color="#003366",
            command=lambda: self.add_transaction_from_income_entry(),
        ).pack(side="left", padx=5)

        # ---------------- Left Panel ----------------
        left = ctk.CTkFrame(main)
        left.pack(side="left", fill="y", padx=10)

        center = ctk.CTkFrame(main)
        center.pack(side="left", expand=True, fill="both")

        right = ctk.CTkFrame(main, fg_color="#cce6ff")
        right.pack(side="right", fill="y", padx=10)

        # ---------------- Transaction Inputs ----------------
        self.amount_entry = ctk.CTkEntry(left, placeholder_text="Amount")
        self.amount_entry.pack(pady=5)

        self.category_var = tk.StringVar(value=self.get_all_categories()[0])
        self.category_dropdown = ttk.Combobox(
            left,
            textvariable=self.category_var,
            values=self.get_all_categories(),
            state="readonly",
        )
        self.category_dropdown.pack(pady=5)

        self.date_entry = ctk.CTkEntry(left)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.pack(pady=5)

        # Add Expense button first
        ctk.CTkButton(
            left, text="Add Expense", command=lambda: self.add_transaction("expense")
        ).pack(pady=3)

        # ---------------- Center Listbox ----------------
        # Filter frame in center above the listbox
        filter_frame = ctk.CTkFrame(center, fg_color="#e6f2ff")
        filter_frame.pack(fill="x", pady=5)

        # Category filter
        self.filter_category = tk.StringVar(value="All")

        self.filter_dropdown = ttk.Combobox(
            filter_frame,
            textvariable=self.filter_category,
            values=["All"] + self.get_all_categories(),
            state="readonly",
        )
        self.filter_dropdown.pack(side="left", padx=5, pady=5)

        # Date filter
        self.filter_date = ctk.CTkEntry(filter_frame, placeholder_text="YYYY-MM-DD")
        self.filter_date.pack(side="left", padx=5, pady=5)

        # Apply / Clear buttons
        ctk.CTkButton(
            filter_frame, text="Apply Filter", command=self.load_transactions
        ).pack(side="left", padx=5, pady=5)
        ctk.CTkButton(
            filter_frame, text="Clear Filter", command=self.clear_filters
        ).pack(side="left", padx=5, pady=5)

        # Listbox for transactions
        self.transaction_list = tk.Listbox(center)
        self.transaction_list.pack(fill="both", expand=True, pady=(0, 10))

        # Delete button below listbox
        ctk.CTkButton(
            center, text="Delete Selected", command=self.delete_transaction
        ).pack(pady=5)

        # ---------------- Right Budget Overview ----------------
        ctk.CTkLabel(
            right,
            text="Budget Overview",
            font=("Arial", 18, "bold"),
            text_color="#003366",  # 🔵 Dark blue
        ).pack(pady=10)

        self.toggle_btn = ctk.CTkButton(
            right, text="Follow Budget: ON", command=self.toggle_budget
        )
        self.toggle_btn.pack(pady=5)

        # Budget Overview (colored)
        self.budget_labels = {}
        for cat in self.get_all_categories():
            lbl = ctk.CTkLabel(right, text=f"{cat}: $0 / $0", text_color="black")
            lbl.pack(pady=2)
            self.budget_labels[cat] = lbl

    def add_custom_category_to_overview(self, cat):
        right = self.budget_labels[next(iter(self.budget_labels))].master

        lbl = ctk.CTkLabel(right, text=f"{cat}: $0 / $0", text_color="black")
        lbl.pack(pady=2)

        self.budget_labels[cat] = lbl

    #
    def add_transaction_from_income_entry(self):
        try:
            amount = float(self.income_entry.get())
        except:
            messagebox.showerror("Error", "Invalid number")
            return

        if amount <= 0:
            messagebox.showerror("Error", "Income must be positive")
            return

        date = datetime.now().strftime("%Y-%m-%d")
        if not self.user_id:  # Guest
            tid = self.next_guest_tid
            self.next_guest_tid += 1
            self.guest_transactions.append((tid, amount, "Income", date, "income"))
        else:
            self.db.add_transaction(self.user_id, amount, "Income", date, "income")

        self.income_entry.delete(0, tk.END)
        self.load_transactions()

    # ---------------- LOGIC ----------------
    def toggle_budget(self):
        self.follow_budget = not self.follow_budget

        if self.follow_budget:
            self.toggle_btn.configure(text="Follow Budget: ON", fg_color="green")
        else:
            self.toggle_btn.configure(text="Follow Budget: OFF", fg_color="red")

        self.update_budget()

    def add_transaction(self, t):
        is_guest = not self.user_id

        try:
            amount = float(self.amount_entry.get())
        except:
            messagebox.showerror("Error", "Invalid number")
            return

        if t == "expense":
            amount = -amount

        category = self.category_var.get() if t == "expense" else "Income"
        date = self.date_entry.get()

        # Budget enforcement only for expenses
        if t == "expense" and self.follow_budget:
            limit = (
                self.guest_budgets.get(category, 0)
                if is_guest
                else self.budgets.get(category, 0)
            )
            rows = (
                self.guest_transactions
                if is_guest
                else self.db.get_all_transactions(self.user_id)
            )
            spent = sum(abs(a) for _, a, c, _, _ in rows if c == category and a < 0)

            if limit > 0 and spent + abs(amount) > limit:
                over = spent + abs(amount) - limit
                messagebox.showerror("Blocked", f"Budget exceeded by ${over:.2f}!")
                return

        # Save transaction
        if is_guest:
            tid = len(self.guest_transactions) + 1
            self.guest_transactions.append((tid, amount, category, date, t))
        else:
            self.db.add_transaction(self.user_id, amount, category, date, t)

        self.load_transactions()

    #
    def clear_filters(self):
        self.filter_category.set("All")
        self.filter_date.delete(0, tk.END)
        self.load_transactions()

    def load_transactions(self):
        self.transaction_list.delete(0, tk.END)

        rows = (
            self.guest_transactions
            if not self.user_id
            else self.db.get_all_transactions(self.user_id)
        )
        balance = 0

        for tid, amt, cat, date, t in rows:
            # Category filter
            if (
                getattr(self, "filter_category", tk.StringVar(value="All")).get()
                != "All"
                and cat != self.filter_category.get()
            ):
                continue

            # Date filter
            if (
                getattr(self, "filter_date", tk.Entry()).get()
                and date != self.filter_date.get()
            ):
                continue

            balance += amt
            display_text = (
                f"(Guest) {cat} | {amt:.2f} | {date}"
                if not self.user_id
                else f"{tid} | {cat} | {amt:.2f} | {date}"
            )
            self.transaction_list.insert(tk.END, display_text)

        self.balance_label.configure(text=f"Balance: ${balance:.2f}")
        self.update_budget()

    def delete_transaction(self):
        selection = self.transaction_list.curselection()

        if not selection:
            messagebox.showwarning("Warning", "Please select a transaction.")
            return

        confirm = messagebox.askyesno(
            "Confirm Delete", "Are you sure you want to delete this transaction?"
        )
        if not confirm:
            return

        index = selection[0]

        try:
            if not self.user_id:  # Guest
                del self.guest_transactions[index]
            else:
                # Create a list of DB IDs in same order as listbox
                db_ids = [t[0] for t in self.db.get_all_transactions(self.user_id)]
                tid = db_ids[index]
                self.db.delete_transaction(self.user_id, tid)

            self.load_transactions()
            messagebox.showinfo("Deleted", "Transaction deleted successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete: {e}")

    # ---------------- BUDGET ----------------
    def setup_budgets_tab(self):

        self.budget_container = ctk.CTkFrame(self.budgets_tab, fg_color="#cce6ff")
        self.budget_container.pack(pady=20)

        # 🔥 ADD CATEGORY INPUT (TOP)
        top = ctk.CTkFrame(self.budget_container, fg_color="#cce6ff")
        top.pack(pady=10)

        self.new_category_entry = ctk.CTkEntry(top, placeholder_text="New Category")
        self.new_category_entry.pack(side="left", padx=5)

        ctk.CTkButton(top, text="Add Category", command=self.handle_add_category).pack(
            side="left", padx=5
        )

        self.budget_entries = {}

        for cat in self.get_all_categories():
            top = ctk.CTkFrame(self.budget_container, fg_color="#cce6ff")
            top.pack(pady=5)

            ctk.CTkLabel(
                top,
                text=cat,
                width=120,
                text_color="#002244",
            ).pack(side="left", padx=5)

            entry = ctk.CTkEntry(top)
            entry.insert(0, "0")
            entry.pack(side="left")

            self.budget_entries[cat] = entry
        # ✅ RIGHT PLACE
        ctk.CTkButton(
            self.budget_container, text="Save Budgets", command=self.save_budgets
        ).pack(pady=10)

    # Handle Add Category button click
    def handle_add_category(self):
        cat = self.new_category_entry.get().strip()

        if not cat:
            messagebox.showerror("Error", "Enter a category name")
            return

        if cat in self.get_all_categories():
            messagebox.showerror("Error", "Category already exists")
            return

        self.add_custom_category(cat)
        self.new_category_entry.delete(0, tk.END)

    # ---------------- ADD CUSTOM CATEGORY TO BUDGET TAB ----------------
    def add_custom_category_to_budget_tab(self, cat):
        container = self.budgets_tab.winfo_children()[0]  # main container

        row = ctk.CTkFrame(container, fg_color="#cce6ff")
        row.pack(pady=5)

        ctk.CTkLabel(row, text=cat, width=120, text_color="#002244").pack(
            side="left", padx=5
        )

        entry = ctk.CTkEntry(row)
        entry.insert(0, "0")
        entry.pack(side="left")

        self.budget_entries[cat] = entry

    def update_budget(self):
        rows = (
            self.guest_transactions
            if not self.user_id
            else self.db.get_all_transactions(self.user_id)
        )

        for cat in self.get_all_categories():
            spent = sum(abs(a) for _, a, c, _, _ in rows if c == cat and a < 0)
            limit = (
                self.guest_budgets.get(cat, 0)
                if not self.user_id
                else self.budgets.get(cat, 0)
            )

            if not self.follow_budget:
                text = f"{cat}: IGNORED"
                color = "gray"
            else:
                text = f"{cat}: ${spent:.2f} / ${limit:.2f}"
                if spent > limit and limit > 0:
                    color = "red"
                    text += " (OVER)"
                elif 0 < limit - spent <= 10:
                    color = "orange"
                else:
                    color = "green"

            if hasattr(self, "budget_labels") and cat in self.budget_labels:
                self.budget_labels[cat].configure(text=text, text_color=color)

    def save_budgets(self):
        is_guest = not self.user_id

        # Save entered budgets
        for cat, entry in self.budget_entries.items():
            try:
                value = float(entry.get())
            except:
                value = 0

            if is_guest:
                self.guest_budgets[cat] = value
            else:
                self.budgets[cat] = value

        # ✅ Ensure ALL categories exist (including custom)
        for cat in self.get_all_categories():
            if is_guest:
                if cat not in self.guest_budgets:
                    self.guest_budgets[cat] = 0
            else:
                if cat not in self.budgets:
                    self.budgets[cat] = 0

        self.update_budget()

        if is_guest:
            messagebox.showinfo("Saved", "Budgets updated (Guest Mode)")
        else:
            messagebox.showinfo("Saved", "Budgets updated")

    # ---------------- PIE CHARTS ----------------
    def show_expense_pie_chart(self):
        rows = (
            self.guest_transactions
            if not self.user_id
            else self.db.get_all_transactions(self.user_id)
        )
        if not rows:
            messagebox.showinfo("No Expenses", "No expense data available.")
            return

        category_totals = {}
        for _, amount, category, _, _ in rows:
            if amount < 0:
                category_totals[category] = category_totals.get(category, 0) + abs(
                    amount
                )

        if not category_totals:
            messagebox.showinfo("No Expenses", "No expense data available.")
            return

        plt.figure(figsize=(6, 6))
        plt.pie(
            category_totals.values(), labels=category_totals.keys(), autopct="%1.1f%%"
        )
        plt.title("Expense Breakdown by Category")
        plt.show()

    def show_income_expense_pie(self):
        rows = (
            self.guest_transactions
            if not self.user_id
            else self.db.get_all_transactions(self.user_id)
        )
        if not rows:
            messagebox.showerror("Error", "No data available.")
            return

        totals = {"Income": 0, "Expenses": 0}
        for _, amount, _, _, _ in rows:
            if amount >= 0:
                totals["Income"] += amount
            else:
                totals["Expenses"] += abs(amount)

        plt.figure(figsize=(6, 6))
        plt.pie(
            totals.values(),
            labels=totals.keys(),
            autopct="%1.1f%%",
            colors=["green", "red"],
        )
        plt.title("Income vs Expenses")
        plt.show()

    # ---------------- REPORTS ----------------
    def setup_reports_tab(self):

        ctk.CTkButton(
            self.reports_tab, text="Bar Chart", command=self.show_bar_chart
        ).pack(pady=10)

        ctk.CTkButton(
            self.reports_tab,
            text="Expense Pie Chart",
            command=self.show_expense_pie_chart,
        ).pack(pady=10)

        ctk.CTkButton(
            self.reports_tab,
            text="Income vs Expense",
            command=self.show_income_expense_pie,
        ).pack(pady=10)

        ctk.CTkButton(
            self.reports_tab, text="Export CSV", command=self.export_csv
        ).pack(pady=10)

        ctk.CTkButton(
            self.reports_tab,
            text="RESET DATA",
            fg_color="#ff4d4d",
            text_color="black",
            command=self.reset_data,
        ).pack(pady=30)

    def show_bar_chart(self):
        rows = (
            self.guest_transactions
            if not self.user_id
            else self.db.get_all_transactions(self.user_id)
        )
        if not rows:
            messagebox.showinfo("No Data", "No transactions available.")
            return

        daily = {}
        for _, amt, _, date, _ in rows:
            daily[date] = daily.get(date, 0) + amt

        plt.bar(daily.keys(), daily.values())
        plt.xticks(rotation=45)
        plt.title("Daily Net Balance")
        plt.show()

    def export_csv(self):
        rows = (
            self.guest_transactions
            if not self.user_id
            else self.db.get_all_transactions(self.user_id)
        )

        if not rows:
            messagebox.showinfo("No Data", "No transactions to export.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Save CSV File",
        )
        if not file_path:
            return

        try:
            with open(file_path, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Type", "Amount", "Category", "Date"])
                for t in rows:
                    tid, amt, cat, date, ttype = t
                    writer.writerow([tid, ttype, amt, cat, date])

            messagebox.showinfo("Exported", f"CSV saved to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export CSV:\n{e}")

    def reset_data(self):
        confirm = messagebox.askyesno("Warning", "Delete ALL data?")
        if not confirm:
            return

        confirm2 = messagebox.askyesno("Final Warning", "This is permanent. Continue?")
        if not confirm2:
            return

        if not self.user_id:  # Guest
            self.guest_transactions.clear()
            self.guest_budgets = {cat: 0 for cat in self.get_all_categories()}
        else:  # Regular user
            self.db.reset_user_transactions(self.user_id)

        self.load_transactions()
        self.update_budget()
        messagebox.showinfo("Deleted", "All data erased.")
