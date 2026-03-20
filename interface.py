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
        self.categories = [
            "Groceries",
            "Gas",
            "Rent",
            "Entertainment",
            "Savings",
            "Misc",
        ]

        self.budgets = {cat: 0 for cat in self.categories}
        self.guest_budgets = {cat: 0 for cat in self.categories}  # Guest budgets
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
        ctk.CTkLabel(self.dashboard_tab, text="Cash Captain", font=("Arial", 30)).pack(
            pady=20
        )
        self.balance_label = ctk.CTkLabel(
            self.dashboard_tab, text="Balance: $0.00", font=("Arial", 22)
        )
        self.balance_label.pack(pady=10)
        ctk.CTkButton(
            self.dashboard_tab, text="Refresh", command=self.load_transactions
        ).pack(pady=10)

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

        self.category_var = tk.StringVar(value=self.categories[0])
        ttk.Combobox(
            left,
            textvariable=self.category_var,
            values=self.categories,
            state="readonly",
        ).pack(pady=5)

        self.date_entry = ctk.CTkEntry(left)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.pack(pady=5)

        # Add Expense button first
        ctk.CTkButton(
            left, text="Add Expense", command=lambda: self.add_transaction("expense")
        ).pack(pady=3)

        # ---------------- Transaction Filters (move to bottom) ----------------
        filter_frame = ctk.CTkFrame(left, fg_color="#e6f2ff")  # optional frame
        self.filter_category = tk.StringVar(value="All")
        ttk.Combobox(
            left,
            textvariable=self.filter_category,
            values=["All"] + self.categories,
            state="readonly",
        ).pack(pady=5)

        # ---------------- Center Listbox ----------------
        # Filter frame in center above the listbox
        filter_frame = ctk.CTkFrame(center, fg_color="#e6f2ff")
        filter_frame.pack(fill="x", pady=5)

        # Category filter
        self.filter_category = tk.StringVar(value="All")
        ttk.Combobox(
            filter_frame,
            textvariable=self.filter_category,
            values=["All"] + self.categories,
            state="readonly",
        ).pack(side="left", padx=5, pady=5)

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
        for cat in self.categories:
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
            tid = len(self.guest_transactions) + 1
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
        try:
            sel = self.transaction_list.get(self.transaction_list.curselection())
            tid = sel.split("|")[0].strip()
            self.db.delete_transaction(self.user_id, tid)
            self.load_transactions()
        except:
            pass

    # ---------------- BUDGET ----------------
    def setup_budgets_tab(self):

        container = ctk.CTkFrame(self.budgets_tab, fg_color="#cce6ff")
        container.pack(pady=20)

        self.budget_entries = {}

        for cat in self.categories:
            row = ctk.CTkFrame(container, fg_color="#cce6ff")
            row.pack(pady=5)

            ctk.CTkLabel(
                row,
                text=cat,
                width=120,
                text_color="#002244",
            ).pack(side="left", padx=5)

            entry = ctk.CTkEntry(row)
            entry.insert(0, "0")
            entry.pack(side="left")

            self.budget_entries[cat] = entry

        ctk.CTkButton(container, text="Save Budgets", command=self.save_budgets).pack(
            pady=10
        )

        ctk.CTkButton(
            container, text="Expense Pie Chart", command=self.show_expense_pie_chart
        ).pack(pady=10)

    def update_budget(self):
        rows = (
            self.guest_transactions
            if not self.user_id
            else self.db.get_all_transactions(self.user_id)
        )

        for cat in self.categories:
            spent = sum(abs(a) for _, a, c, _, _ in rows if c == cat and a < 0)
            limit = self.guest_budgets[cat] if not self.user_id else self.budgets[cat]

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
        if not self.user_id:  # Guest mode
            for cat, entry in self.budget_entries.items():
                try:
                    self.guest_budgets[cat] = float(entry.get())
                except:
                    self.guest_budgets[cat] = 0
            self.update_budget()
            messagebox.showinfo("Saved", "Budgets updated (Guest Mode)")
            return

        # Regular user
        for cat, entry in self.budget_entries.items():
            try:
                self.budgets[cat] = float(entry.get())
            except:
                self.budgets[cat] = 0

        self.update_budget()
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
            text="DELETE ALL DATA",
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
            messagebox.showinfo("No Data", "Nothing to export.")
            return

        file = filedialog.asksaveasfilename(defaultextension=".csv")
        if not file:
            return

        with open(file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Amount", "Category", "Date", "Type"])
            writer.writerows(rows)

        messagebox.showinfo("Export", "CSV Exported")

    def reset_data(self):
        confirm = messagebox.askyesno("Warning", "Delete ALL data?")
        if not confirm:
            return

        confirm2 = messagebox.askyesno("Final Warning", "This is permanent. Continue?")
        if not confirm2:
            return

        if not self.user_id:  # Guest
            self.guest_transactions.clear()
            self.guest_budgets = {cat: 0 for cat in self.categories}
        else:  # Regular user
            self.db.reset_user_transactions(self.user_id)

        self.load_transactions()
        self.update_budget()
        messagebox.showinfo("Deleted", "All data erased.")
