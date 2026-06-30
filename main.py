"""
Personal Expense Tracker - Tkinter GUI Version
------------------------------------------------
A desktop application (Tkinter) to track daily expenses and income,
store data persistently in JSON, and display financial summaries.

Author: Nagina
"""

import json
import os
from datetime import datetime
from collections import defaultdict
import tkinter as tk
from tkinter import ttk, messagebox

DATA_FILE = "expenses_data.json"


# ---------------- Data Layer ----------------
class Transaction:
    def __init__(self, t_type, category, amount, note="", date=None):
        self.t_type = t_type
        self.category = category
        self.amount = amount
        self.note = note
        self.date = date or datetime.now().strftime("%Y-%m-%d")

    def to_dict(self):
        return {
            "type": self.t_type,
            "category": self.category,
            "amount": self.amount,
            "note": self.note,
            "date": self.date,
        }

    @staticmethod
    def from_dict(data):
        return Transaction(
            data["type"], data["category"], data["amount"],
            data.get("note", ""), data["date"]
        )


class ExpenseTracker:
    def __init__(self, filename=DATA_FILE):
        self.filename = filename
        self.transactions = []
        self.load_data()

    def load_data(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as f:
                    raw = json.load(f)
                self.transactions = [Transaction.from_dict(t) for t in raw]
            except (json.JSONDecodeError, KeyError):
                self.transactions = []
        else:
            self.transactions = []

    def save_data(self):
        with open(self.filename, "w") as f:
            json.dump([t.to_dict() for t in self.transactions], f, indent=4)

    def add_transaction(self, t_type, category, amount, note=""):
        self.transactions.append(Transaction(t_type, category, amount, note))
        self.save_data()

    def delete_transaction(self, index):
        if 0 <= index < len(self.transactions):
            self.transactions.pop(index)
            self.save_data()

    def total_income(self):
        return sum(t.amount for t in self.transactions if t.t_type == "income")

    def total_expense(self):
        return sum(t.amount for t in self.transactions if t.t_type == "expense")

    def balance(self):
        return self.total_income() - self.total_expense()

    def category_summary(self):
        summary = defaultdict(float)
        for t in self.transactions:
            sign = 1 if t.t_type == "income" else -1
            summary[t.category] += sign * t.amount
        return summary

    def monthly_summary(self):
        summary = defaultdict(lambda: {"income": 0.0, "expense": 0.0})
        for t in self.transactions:
            month = t.date[:7]
            summary[month][t.t_type] += t.amount
        return dict(sorted(summary.items()))


# ---------------- GUI Layer ----------------
class ExpenseTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Personal Expense Tracker")
        self.geometry("820x560")
        self.minsize(760, 500)
        self.configure(bg="#f4f6f8")

        self.tracker = ExpenseTracker()

        self._build_style()
        self._build_top_summary()
        self._build_form()
        self._build_table()
        self._build_bottom_buttons()

        self.refresh_table()
        self.refresh_summary()

    # ---------- Styling ----------
    def _build_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Treeview", rowheight=26, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("TButton", font=("Segoe UI", 10), padding=6)
        style.configure("TLabel", font=("Segoe UI", 10), background="#f4f6f8")
        style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"), background="#f4f6f8")

    # ---------- Top summary cards ----------
    def _build_top_summary(self):
        frame = tk.Frame(self, bg="#f4f6f8")
        frame.pack(fill="x", padx=15, pady=(15, 5))

        self.income_var = tk.StringVar(value="Income: 0.00")
        self.expense_var = tk.StringVar(value="Expense: 0.00")
        self.balance_var = tk.StringVar(value="Balance: 0.00")

        self._make_card(frame, self.income_var, "#2e7d32").pack(side="left", expand=True, fill="x", padx=5)
        self._make_card(frame, self.expense_var, "#c62828").pack(side="left", expand=True, fill="x", padx=5)
        self._make_card(frame, self.balance_var, "#1565c0").pack(side="left", expand=True, fill="x", padx=5)

    def _make_card(self, parent, textvar, color):
        card = tk.Frame(parent, bg=color, padx=10, pady=12)
        label = tk.Label(card, textvariable=textvar, bg=color, fg="white",
                          font=("Segoe UI", 12, "bold"))
        label.pack()
        return card

    # ---------- Entry form ----------
    def _build_form(self):
        form = tk.LabelFrame(self, text="Add Transaction", bg="#f4f6f8",
                              font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        form.pack(fill="x", padx=15, pady=10)

        # Type
        ttk.Label(form, text="Type:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.type_var = tk.StringVar(value="expense")
        type_combo = ttk.Combobox(form, textvariable=self.type_var,
                                   values=["income", "expense"], state="readonly", width=12)
        type_combo.grid(row=0, column=1, padx=5, pady=5)

        # Category
        ttk.Label(form, text="Category:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.category_entry = ttk.Entry(form, width=18)
        self.category_entry.grid(row=0, column=3, padx=5, pady=5)

        # Amount
        ttk.Label(form, text="Amount:").grid(row=0, column=4, sticky="w", padx=5, pady=5)
        self.amount_entry = ttk.Entry(form, width=12)
        self.amount_entry.grid(row=0, column=5, padx=5, pady=5)

        # Note
        ttk.Label(form, text="Note:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.note_entry = ttk.Entry(form, width=50)
        self.note_entry.grid(row=1, column=1, columnspan=4, sticky="w", padx=5, pady=5)

        add_btn = ttk.Button(form, text="Add", command=self.handle_add)
        add_btn.grid(row=1, column=5, padx=5, pady=5, sticky="e")

    # ---------- Table ----------
    def _build_table(self):
        table_frame = tk.Frame(self, bg="#f4f6f8")
        table_frame.pack(fill="both", expand=True, padx=15, pady=5)

        columns = ("date", "type", "category", "amount", "note")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        headings = {"date": "Date", "type": "Type", "category": "Category",
                    "amount": "Amount", "note": "Note"}
        widths = {"date": 90, "type": 80, "category": 130, "amount": 90, "note": 250}

        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # color tags
        self.tree.tag_configure("income", foreground="#2e7d32")
        self.tree.tag_configure("expense", foreground="#c62828")

    # ---------- Bottom buttons ----------
    def _build_bottom_buttons(self):
        bottom = tk.Frame(self, bg="#f4f6f8")
        bottom.pack(fill="x", padx=15, pady=(0, 15))

        ttk.Button(bottom, text="Delete Selected", command=self.handle_delete).pack(side="left")
        ttk.Button(bottom, text="View Category Summary", command=self.show_category_summary).pack(side="left", padx=8)
        ttk.Button(bottom, text="View Monthly Summary", command=self.show_monthly_summary).pack(side="left")

    # ---------- Logic / Handlers ----------
    def handle_add(self):
        t_type = self.type_var.get()
        category = self.category_entry.get().strip()
        amount_str = self.amount_entry.get().strip()
        note = self.note_entry.get().strip()

        if not category:
            messagebox.showerror("Missing Category", "Please enter a category.")
            return

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Amount", "Please enter a valid positive number for amount.")
            return

        self.tracker.add_transaction(t_type, category, amount, note)

        # clear inputs
        self.category_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.note_entry.delete(0, tk.END)

        self.refresh_table()
        self.refresh_summary()

    def handle_delete(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("No Selection", "Please select a transaction to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", "Delete the selected transaction?")
        if not confirm:
            return

        index = int(self.tree.item(selected[0], "tags")[1])
        self.tracker.delete_transaction(index)
        self.refresh_table()
        self.refresh_summary()

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for i, t in enumerate(self.tracker.transactions):
            self.tree.insert(
                "", "end",
                values=(t.date, t.t_type, t.category, f"{t.amount:.2f}", t.note),
                tags=(t.t_type, str(i))
            )

    def refresh_summary(self):
        self.income_var.set(f"Income: {self.tracker.total_income():.2f}")
        self.expense_var.set(f"Expense: {self.tracker.total_expense():.2f}")
        self.balance_var.set(f"Balance: {self.tracker.balance():.2f}")

    def show_category_summary(self):
        summary = self.tracker.category_summary()
        if not summary:
            messagebox.showinfo("Category Summary", "No transactions yet.")
            return
        lines = [f"{cat:<15}: {amt:+.2f}" for cat, amt in summary.items()]
        messagebox.showinfo("Category Summary", "\n".join(lines))

    def show_monthly_summary(self):
        summary = self.tracker.monthly_summary()
        if not summary:
            messagebox.showinfo("Monthly Summary", "No transactions yet.")
            return
        lines = []
        for month, vals in summary.items():
            net = vals["income"] - vals["expense"]
            lines.append(f"{month}  Income: {vals['income']:.2f}  Expense: {vals['expense']:.2f}  Net: {net:+.2f}")
        messagebox.showinfo("Monthly Summary", "\n".join(lines))


if __name__ == "__main__":
    app = ExpenseTrackerApp()
    app.mainloop()