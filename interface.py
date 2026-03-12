import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import matplotlib.pyplot as plt
import csv

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class FinanceManagerUI:
    """ Cash Captain - Personal Finance Manager GUI """

    def __init__(self, root, db, user_id=None):
        self.root = root
        self.db = db
        self.user_id = user_id

        self.root.title("Cash Captain - Personal Finance Manager")
        self.root.geometry("900x600")

        self.categories = ["Groceries", "Gas", "Savings", "Entertainment", "Rent", "Miscellaneous", "Income"]
        self.budgets = {cat: 0.0 for cat in self.categories}

        self.follow_budget = ctk.BooleanVar(value=True)

        self.create_tabs()
        self.setup_dashboard_tab()
        self.setup_transactions_tab()
        self.setup_budgets_tab()
        self.setup_reports_tab()

        self.load_transactions()

    # -------------------- TABS --------------------

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

    # -------------------- DASHBOARD --------------------

    def setup_dashboard_tab(self):

    # center container
     center_frame = ctk.CTkFrame(self.dashboard_tab, fg_color="transparent")
     center_frame.pack(expand=True)
     
    # title
     title = ctk.CTkLabel(
    center_frame,
        text="Cash Captain",
        font=ctk.CTkFont(family="Segoe UI", size=42, weight="bold")
    )
     title.pack(pady=(10,5))

     subtitle = ctk.CTkLabel(
     center_frame,
        text="Personal Finance Dashboard",
        font=ctk.CTkFont(size=18)
    )
     subtitle.pack(pady=(0,20))

    # balance
     self.balance_label = ctk.CTkLabel(
      center_frame,
        text="Balance: $0.00",
        font=ctk.CTkFont(size=28, weight="bold"),
        text_color="#4da6ff"
    )
     self.balance_label.pack(pady=10)

    # refresh button
     ctk.CTkButton(
      center_frame,
        text="Refresh",
        width=160,
        height=40,
        font=ctk.CTkFont(size=16),
        command=self.load_transactions
    ).pack(pady=10)

    # -------------------- TRANSACTIONS TAB --------------------

    def setup_transactions_tab(self):

        frame = self.transactions_tab

        split_frame = ctk.CTkFrame(frame)
        split_frame.pack(fill="both", expand=True, padx=10, pady=10)

        left_frame = ctk.CTkFrame(split_frame)
        left_frame.pack(side="left", fill="both", expand=True)

        input_frame = ctk.CTkFrame(left_frame)
        input_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(input_frame, text="Amount:").grid(row=0, column=0, sticky="e")

        self.amount_entry = ctk.CTkEntry(input_frame)
        self.amount_entry.grid(row=0, column=1, padx=5)

        ctk.CTkLabel(input_frame, text="Category:").grid(row=1, column=0, sticky="e")

        self.category_var = ctk.StringVar(value=self.categories[0])

        self.category_dropdown = ttk.Combobox(
            input_frame,
            textvariable=self.category_var,
            values=self.categories,
            state="readonly",
            width=20
        )
        self.category_dropdown.grid(row=1, column=1, padx=5)

        ctk.CTkLabel(input_frame, text="Date (YYYY-MM-DD):").grid(row=2, column=0, sticky="e")

        self.date_entry = ctk.CTkEntry(input_frame)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=2, column=1, padx=5)

        ctk.CTkButton(input_frame,
                      text="Add Income",
                      command=lambda: self.add_transaction("income")).grid(row=3, column=0, pady=5)

        ctk.CTkButton(input_frame,
                      text="Add Expense",
                      command=lambda: self.add_transaction("expense")).grid(row=3, column=1, pady=5)

        list_frame = ctk.CTkFrame(left_frame)
        list_frame.pack(fill="both", expand=True, pady=5)

        self.transaction_list = ctk.CTkTextbox(list_frame, height=200)
        self.transaction_list.pack(fill="both", expand=True)

        ctk.CTkButton(left_frame,
                      text="Delete Selected Transaction",
                      command=self.delete_transaction).pack(pady=5)

        ctk.CTkButton(left_frame,
                      text="Edit Selected Transaction",
                      command=self.open_edit_window).pack(pady=5)

        # ---------------- Budget Overview ----------------

        right_frame = ctk.CTkFrame(split_frame, width=250)
        right_frame.pack(side="right", fill="y", padx=10)
        right_frame.pack_propagate(False)

        ctk.CTkLabel(right_frame,
                     text="Budget Overview",
                     font=("Helvetica", 14)).pack(pady=5)

        self.budget_toggle_btn = ctk.CTkButton(
            right_frame,
            text="Follow Budget: ON",
            fg_color="green",
            hover_color="#0b5e13",
            command=self.toggle_budget_mode
        )
        self.budget_toggle_btn.pack(pady=5)

        self.budget_labels = {}

        for cat in self.categories:
            lbl = ctk.CTkLabel(right_frame,
                               text=f"{cat}: $0.00 / ${self.budgets[cat]:.2f}")
            lbl.pack(anchor="w")
            self.budget_labels[cat] = lbl

    def toggle_budget_mode(self):

        if self.follow_budget.get():
            self.follow_budget.set(False)
            self.budget_toggle_btn.configure(text="Follow Budget: OFF",
                                             fg_color="red")
        else:
            self.follow_budget.set(True)
            self.budget_toggle_btn.configure(text="Follow Budget: ON",
                                             fg_color="green")

        self.update_budget_labels()

    def update_budget_labels(self):

        rows = self.db.get_all_transactions(self.user_id)

        for cat in self.categories:
            spent = sum(abs(a) for _, a, c, _, _ in rows if c == cat and a < 0)

            if self.follow_budget.get():
                self.budget_labels[cat].configure(
                    text=f"{cat}: ${spent:.2f} / ${self.budgets[cat]:.2f}")
            else:
                self.budget_labels[cat].configure(
                    text=f"{cat}: ${spent:.2f} (Budget Ignored)")

    # -------------------- EDIT WINDOW --------------------

    def open_edit_window(self):

        self.edit_win = ctk.CTkToplevel(self.root)
        self.edit_win.title("Edit Transaction")
        self.edit_win.geometry("350x250")

        ctk.CTkLabel(self.edit_win, text="Amount:").pack()
        self.edit_amount = ctk.CTkEntry(self.edit_win)
        self.edit_amount.pack()

        ctk.CTkLabel(self.edit_win, text="Category:").pack()

        self.edit_category_var = ctk.StringVar(value=self.categories[0])

        self.edit_category_dropdown = ttk.Combobox(
            self.edit_win,
            textvariable=self.edit_category_var,
            values=self.categories,
            state="readonly"
        )
        self.edit_category_dropdown.pack()

        ctk.CTkLabel(self.edit_win, text="Date:").pack()

        self.edit_date = ctk.CTkEntry(self.edit_win)
        self.edit_date.pack()

        ctk.CTkButton(self.edit_win,
                      text="Save Changes",
                      command=self.save_transaction_edits).pack(pady=10)
    def save_transaction_edits(self):
        try:
            amount = float(self.edit_amount.get().replace("+", ""))
        except ValueError:
            messagebox.showerror("Error", "Amount must be numeric.")
            return
        category = self.edit_category_var.get()
        date = self.edit_date.get().strip()
        self.db.update_transaction(self.user_id, self.edit_id, amount, category, date)
        self.edit_win.destroy()
        self.load_transactions()
        messagebox.showinfo("Updated", "Transaction updated successfully!")

    # -------------------- ADD/DELETE/LOAD TRANSACTIONS --------------------
    def add_transaction(self, t_type):
        try:
            amount = float(self.amount_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Enter a valid number.")
            return

        date = self.date_entry.get().strip() or datetime.now().strftime("%Y-%m-%d")

        if t_type == "income":
            self.db.add_transaction(self.user_id, amount, "Income", date, t_type)
        else:
            category = self.category_var.get()
            amount = -amount

            if self.follow_budget.get():
                rows = self.db.get_all_transactions(self.user_id)
                spent = sum(abs(a) for _, a, c, _, _ in rows if c == category and a < 0)
                limit = self.budgets.get(category, 0)
                remaining = limit - spent

                if -amount > remaining:
                    messagebox.showwarning(
                        "Budget Limit Reached",
                        f"Cannot add this expense. You're ${abs(-amount - remaining):.2f} over the budget for {category}."
                    )
                    return
                elif remaining - abs(-amount) <= 10:
                    messagebox.showinfo(
                        "Near Budget Limit",
                        f"Warning: You are within $10 of the budget for {category}!"
                    )

            self.db.add_transaction(self.user_id, amount, category, date, t_type)

        self.amount_entry.delete(0, tk.END)
        self.load_transactions()

    def delete_transaction(self):
        try:
            selected = self.transaction_list.get(self.transaction_list.curselection())
            tid = selected.split(" | ")[0]
        except:
            messagebox.showerror("Error", "Select a transaction to delete.")
            return
        self.db.delete_transaction(self.user_id, tid)
        self.load_transactions()
        messagebox.showinfo("Deleted", "Transaction removed.")

    def load_transactions(self):
        self.transaction_list.delete(0, tk.END)
        rows = self.db.get_all_transactions(self.user_id)
        balance = 0
        for tid, amount, cat, date, ttype in rows:
            balance += amount
            if ttype == "income":
                display_text = f"{tid} | Income | {amount:.2f} | {date}"
            else:
                display_text = f"{tid} | {cat} | {amount:.2f} | {date}"
            self.transaction_list.insert(tk.END, display_text)

        self.balance_label.config(text=f"Balance: ${balance:.2f}")
        self.update_dashboard()
        self.update_budget_labels()

    # -------------------- BUDGETS TAB --------------------
    def setup_budgets_tab(self):
        frame = self.budgets_tab
        tk.Label(frame, text="Set Budgets by Category", font=("Helvetica", 16)).pack(pady=10)
        container = tk.Frame(frame)
        container.pack()
        self.budget_entries = {}
        for i, cat in enumerate(self.categories):
            tk.Label(container, text=f"{cat}:", width=15, anchor="e").grid(row=i, column=0, padx=5)
            entry = tk.Entry(container, width=10)
            entry.insert(0, "0")
            entry.grid(row=i, column=1)
            self.budget_entries[cat] = entry
        tk.Button(frame, text="Save Budgets", command=self.save_budgets).pack(pady=10)

    def save_budgets(self):
        for cat, entry in self.budget_entries.items():
            try:
                self.budgets[cat] = float(entry.get())
            except ValueError:
                self.budgets[cat] = 0.0
        self.update_budget_labels()
        messagebox.showinfo("Saved", "Budgets saved successfully!")

    # -------------------- REPORTS TAB --------------------
    def setup_reports_tab(self):
     frame = self.reports_tab

     tk.Label(frame, text="Reports & Export", font=("Helvetica", 16)).pack(pady=10)

     tk.Button(
        frame,
        text="Bar Chart: Daily Net Amount",
        command=self.show_bar_chart
     ).pack(pady=10)

     tk.Button(
        frame,
        text="Pie Chart: Spending by Category",
        command=self.show_expense_pie_chart
     ).pack(pady=10)

     tk.Button(
        frame,
        text="Pie Chart: Income vs Expenses",
        command=self.show_income_expense_pie
     ).pack(pady=10)

     tk.Button(
        frame,
        text="Export All Transactions to CSV",
        command=self.export_csv
     ).pack(pady=10)

     tk.Button(
        frame,
        text="Reset ALL Data (Dangerous)",
        fg="red",
        command=self.reset_data_warning
     ).pack(pady=10)

    # -------------------- BAR GRAPH --------------------
    def show_bar_chart(self):
        rows = self.db.get_all_transactions(self.user_id)

        if not rows:
            messagebox.showerror("Error", "No data available.")
            return

        daily_totals = {}

        for _, amount, category, date, t_type in rows:

            if t_type == "expense":
                amount = -abs(amount)
            elif t_type == "income":
                amount = abs(amount)

            if date not in daily_totals:
                daily_totals[date] = 0

            daily_totals[date] += amount

        dates = sorted(daily_totals.keys())
        values = [daily_totals[d] for d in dates]

        plt.figure(figsize=(9,4))
        plt.bar(dates, values)

        plt.axhline(0)

        plt.title("Daily Net Cash Flow")
        plt.xlabel("Date")
        plt.ylabel("Net Amount")

        plt.xticks(rotation=45)

        plt.tight_layout()
        plt.show()

    # -------------------- PIE CHART --------------------
    def show_expense_pie_chart(self):
        rows = self.db.get_all_transactions(self.user_id)
        if not rows:
            messagebox.showerror("Error", "No data available.")
            return
        category_totals = {}
        for _, amount, category, _, _ in rows:
            if amount < 0:
                category_totals[category] = category_totals.get(category,0)+abs(amount)
        if not category_totals:
            messagebox.showinfo("No Expenses", "No expense data available.")
            return
        labels = list(category_totals.keys())
        values = list(category_totals.values())
        plt.figure(figsize=(6,6))
        plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)
        plt.title("Expense Breakdown by Category")
        plt.tight_layout()
        plt.show()

    def show_income_expense_pie(self):
        rows = self.db.get_all_transactions(self.user_id)
        if not rows:
            messagebox.showerror("Error", "No data available.")
            return
        totals = {"Income":0,"Expenses":0}
        for _, amount, _, _, _ in rows:
            if amount >= 0:
                totals["Income"] += amount
            else:
                totals["Expenses"] += abs(amount)
        if totals["Income"]==0 and totals["Expenses"]==0:
            messagebox.showinfo("No Data", "No transactions to display.")
            return
        labels = list(totals.keys())
        values = list(totals.values())
        plt.figure(figsize=(6,6))
        plt.pie(values, labels=labels, autopct='%1.1f%%', colors=["green","red"], startangle=140)
        plt.title("Income vs Expenses")
        plt.tight_layout()
        plt.show()
    # -------------------- CSV EXPORT --------------------
    def export_csv(self):
        filename = filedialog.asksaveasfilename(title="Save CSV", defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if not filename:
            return
        rows = self.db.get_all_transactions(self.user_id)
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Amount", "Category", "Date", "Type"])
            writer.writerows(rows)
        messagebox.showinfo("Export Complete", f"Saved to:\n{filename}")

    # -------------------- RESET DATA --------------------
    def reset_data_warning(self):
        msg = "⚠ WARNING: This will delete ALL your transactions.\n\nAre you sure?"
        confirm = messagebox.askyesno("Confirm Reset", msg)
        if confirm:
            self.reset_all_data()

    def reset_all_data(self):
        self.db.reset_user_transactions(self.user_id)
        self.load_transactions()
        messagebox.showinfo("Database Reset", "All transactions have been deleted.")
