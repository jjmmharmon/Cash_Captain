import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import matplotlib.pyplot as plt
import csv


class FinanceManagerUI:
    """ Cash Captain - Personal Finance Manager GUI
    Works with both logged-in users and guest sessions.
    """
    def __init__(self, root, db, user_id=None):
        self.root = root
        self.db = db
        self.user_id = user_id

        self.root.title("Cash Captain - Personal Finance Manager")
        self.root.geometry("900x600")

        self.categories = ["Groceries", "Gas", "Savings", "Entertainment", "Rent", "Miscellaneous", "Income"]
        self.budgets = {cat: 0.0 for cat in self.categories}

        self.create_tabs()
        self.setup_dashboard_tab()
        self.setup_transactions_tab()
        self.setup_budgets_tab()
        self.setup_reports_tab()

        self.load_transactions()  # This must exist by now


    # TABS


    def create_tabs(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both")

        self.dashboard_tab = ttk.Frame(self.notebook)
        self.transactions_tab = ttk.Frame(self.notebook)
        self.budgets_tab = ttk.Frame(self.notebook)
        self.reports_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.notebook.add(self.transactions_tab, text="Transactions")
        self.notebook.add(self.budgets_tab, text="Budgets")
        self.notebook.add(self.reports_tab, text="Reports")



    # DASHBOARD TAB

 
    def setup_dashboard_tab(self):
        tk.Label(self.dashboard_tab, text="Cash Captain Dashboard", font=("Helvetica", 18)).pack(pady=20)
        self.balance_label = tk.Label(self.dashboard_tab, text="Balance: $0.00", font=("Helvetica", 16), fg="blue")
        self.balance_label.pack(pady=10)
        tk.Button(self.dashboard_tab, text="Refresh", command=self.load_transactions).pack(pady=5)

    def update_dashboard(self):
        rows = self.db.get_all_transactions(self.user_id)
        balance = sum(amount for _, amount, _, _, _ in rows)
        self.balance_label.config(text=f"Balance: ${balance:.2f}")

    # TRANSACTIONS TAB


    def setup_transactions_tab(self):
        frame = self.transactions_tab

        # Add Transaction
        input_frame = tk.LabelFrame(frame, text="Add Transaction")
        input_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(input_frame, text="Amount:").grid(row=0, column=0, sticky="e")
        self.amount_entry = tk.Entry(input_frame)
        self.amount_entry.grid(row=0, column=1, padx=5)

        tk.Label(input_frame, text="Category:").grid(row=1, column=0, sticky="e")
        self.category_var = tk.StringVar(value=self.categories[0])
        self.category_dropdown = ttk.Combobox(input_frame, textvariable=self.category_var, values=self.categories, state="readonly", width=20)
        self.category_dropdown.grid(row=1, column=1, padx=5)

        tk.Label(input_frame, text="Date (YYYY-MM-DD):").grid(row=2, column=0, sticky="e")
        self.date_entry = tk.Entry(input_frame)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=2, column=1, padx=5)

        tk.Button(input_frame, text="Add Income", command=lambda: self.add_transaction("income")).grid(row=3, column=0, pady=10)
        tk.Button(input_frame, text="Add Expense", command=lambda: self.add_transaction("expense")).grid(row=3, column=1, pady=10)

        # Filter
        filter_frame = tk.LabelFrame(frame, text="Filter Transactions")
        filter_frame.pack(fill="x", padx=10)

        tk.Label(filter_frame, text="Category:").grid(row=0, column=0)
        self.filter_category_var = tk.StringVar(value="All")
        self.filter_category_dropdown = ttk.Combobox(filter_frame, textvariable=self.filter_category_var, values=["All"] + self.categories, state="readonly", width=20)
        self.filter_category_dropdown.grid(row=0, column=1, padx=5)

        tk.Label(filter_frame, text="Start Date:").grid(row=1, column=0)
        self.filter_start_entry = tk.Entry(filter_frame)
        self.filter_start_entry.grid(row=1, column=1, padx=5)

        tk.Label(filter_frame, text="End Date:").grid(row=1, column=2)
        self.filter_end_entry = tk.Entry(filter_frame)
        self.filter_end_entry.grid(row=1, column=3, padx=5)

        tk.Button(filter_frame, text="Apply Filter", command=self.load_transactions).grid(row=0, column=3, padx=5)

        # Listbox
        list_frame = tk.Frame(frame)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.transaction_list = tk.Listbox(list_frame, width=90, height=15)
        self.transaction_list.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame, command=self.transaction_list.yview)
        scrollbar.pack(side="right", fill="y")
        self.transaction_list.config(yscrollcommand=scrollbar.set)

        tk.Button(frame, text="Delete Selected Transaction", command=self.delete_transaction).pack(pady=5)
        tk.Button(frame, text="Edit Selected Transaction", command=self.open_edit_window).pack(pady=5)


    # EDIT TRANSACTION POPUP


    def open_edit_window(self):
        try:
            selected = self.transaction_list.get(self.transaction_list.curselection())
        except:
            messagebox.showerror("Error", "Please select a transaction to edit.")
            return


        tid, category, amount, date = selected.split(" | ")
        amount = amount.replace("+", "")


        self.edit_id = tid


        self.edit_win = tk.Toplevel(self.root)
        self.edit_win.title("Edit Transaction")
        self.edit_win.geometry("350x250")


        tk.Label(self.edit_win, text="Amount:").pack()
        self.edit_amount = tk.Entry(self.edit_win)
        self.edit_amount.insert(0, amount)
        self.edit_amount.pack()


        tk.Label(self.edit_win, text="Category:").pack()
        self.edit_category_var = tk.StringVar(value=category)
        self.edit_category_dropdown = ttk.Combobox(
            self.edit_win, textvariable=self.edit_category_var,
            values=self.categories, state="readonly"
        )
        self.edit_category_dropdown.pack()


        tk.Label(self.edit_win, text="Date:").pack()
        self.edit_date = tk.Entry(self.edit_win)
        self.edit_date.insert(0, date)
        self.edit_date.pack()


        tk.Button(self.edit_win, text="Save Changes",
                  command=self.save_transaction_edits).pack(pady=10)


    def save_transaction_edits(self):
        try:
            amount = float(self.edit_amount.get().replace("+", ""))
        except ValueError:
            messagebox.showerror("Error", "Amount must be numeric.")
            return


        category = self.edit_category_var.get()
        date = self.edit_date.get().strip()


        self.db.update_transaction(self.user_id,self.edit_id,amount,category,date)
        self.edit_win.destroy()
        self.load_transactions()
        messagebox.showinfo("Updated", "Transaction updated successfully!")


    # ADD/DELETE/LOAD TRANSACTIONS


    def add_transaction(self, t_type):
        try:
            amount = float(self.amount_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Enter a valid number.")
            return

        if t_type == "expense":
            amount = -amount

        category = self.category_var.get()
        date = self.date_entry.get().strip()
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")

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

        category = self.filter_category_var.get()
        start = self.filter_start_entry.get().strip()
        end = self.filter_end_entry.get().strip()

        if category == "All":
            category = None
        if start == "":
            start = None
        if end == "":
            end = None

        rows = self.db.get_all_transactions(self.user_id)

        filtered = []
        for t in rows:
            tid, amount, cat, date, ttype = t
            if category and cat != category:
                continue
            if start and date < start:
                continue
            if end and date > end:
                continue
            filtered.append(t)

        balance = 0
        for tid, amount, cat, date, ttype in filtered:
            balance += amount
            self.transaction_list.insert(tk.END, f"{tid} | {cat} | {amount:+.2f} | {date}")

        self.balance_label.config(text=f"Balance: ${balance:.2f}")
        self.update_dashboard()
        self.check_budgets(filtered)    # BUDGETS

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
            except:
                self.budgets[cat] = 0.0
        messagebox.showinfo("Saved", "Budgets updated.")
        self.load_transactions()

    def check_budgets(self, rows):
        spent = {cat: 0.0 for cat in self.categories}
        for _, amount, cat, _, _ in rows:
            if amount < 0:
                spent[cat] += abs(amount)
        warnings = []
        for cat in self.categories:
            if self.budgets[cat] > 0 and spent[cat] > self.budgets[cat]:
                warnings.append(f"{cat}: Spent ${spent[cat]:.2f} / Budget ${self.budgets[cat]:.2f}")
        if warnings:
            messagebox.showwarning("Budget Warning", "Exceeded budgets:\n\n" + "\n".join(warnings))


# REPORTS TAB


    def setup_reports_tab(self):
        frame = self.reports_tab
        tk.Label(frame, text="Reports & Export", font=("Helvetica", 16)).pack(pady=10)
        tk.Button(frame, text="Bar Chart: Daily Net Amount", command=self.show_bar_chart).pack(pady=10)
        tk.Button(frame, text="Export All Transactions to CSV", command=self.export_csv).pack(pady=10)
        tk.Button(frame, text="Reset ALL Data (Dangerous)", fg="red", command=self.reset_data_warning).pack(pady=10)


# BAR GRAPH FUNCTIONS


    def show_bar_chart(self):
        rows = self.db.get_all_transactions(self.user_id)
        if not rows:
            messagebox.showerror("Error", "No data available.")
            return

        daily = {}
        for _, amount, _, date, _ in rows:
            daily[date] = daily.get(date, 0) + amount

        dates = sorted(daily.keys())
        values = [daily[d] for d in dates]

        plt.figure(figsize=(8, 4))
        plt.bar(dates, values)
        plt.title("Daily Net Amount")
        plt.xlabel("Date")
        plt.ylabel("Amount")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()


    def reset_data_warning(self):
        msg = "⚠ WARNING: This will delete ALL your transactions.\n\nAre you sure?"
        confirm = messagebox.askyesno("Confirm Reset", msg)
        if confirm:
            self.reset_all_data()

    def reset_all_data(self):
        self.db.reset_user_transactions(self.user_id)
        self.load_transactions()
        messagebox.showinfo("Database Reset", "All transactions have been deleted.")

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