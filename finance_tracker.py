# a few libraries to handle files, dates, and the graphical interface
# csv for saving, datetime for dates, tkinter for gui
import csv                

# the main GUI library
import tkinter as tk       
# extra widgets and pop‑ups
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog   

# for working with dates
from datetime import date
from datetime import datetime
from datetime import timedelta

# The file where all transactions are stored
FILE_NAME = "alinas_finance.csv"


class FinanceTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Alina's Finance Tracker")
        self.root.geometry("780x580")
        root.resizable(0,0)                          # this removes the maximize button --> no resizing
        self.root.configure(bg="#ADD8E6")          # soft blue background

        # all transactions go here: each is a dict with type,date,description,category,amount
        # { "type": "Income"/"Expense", "date": "2026-02-19", "desc": "...", "category": "...", "amount": 12.34 }

        self.data = [] 
        #  categories – the user can add more later
        self.categories = ["Food", "Travel", "Bills", "Shopping", "Entertainment", "Other"]

        # tkinter variables that keep track of the current choices - food as default
        self.trans_type = tk.StringVar(value="Expense")        
        self.selected_category = tk.StringVar(value=self.categories[0])

        # GUI :

        #  title 
        tk.Label(root, text="Finance Tracker", font=("Arial", 16, "bold"), bg="#ADD8E6").pack(pady=10)

        #  income/expense radio buttons 
        type_frame = tk.Frame(root, bg="#ADD8E6")
        type_frame.pack()
        tk.Radiobutton(type_frame, text="Expense", variable=self.trans_type, value="Expense", bg="#ADD8E6").pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(type_frame, text="Income", variable=self.trans_type, value="Income", bg="#ADD8E6").pack(side=tk.LEFT, padx=10)

        # input form 
        form = tk.Frame(root, bg="#ADD8E6")
        form.pack(pady=10)

        # row 0: Description and category (with "+" button)
        tk.Label(form, text="Description:", width=12, bg="#ADD8E6", anchor="e").grid(row=0, column=0, padx=5, pady=4)
        self.desc_entry = tk.Entry(form, width=25)
        self.desc_entry.grid(row=0, column=1, padx=5, pady=4)

        tk.Label(form, text="Category:", width=12, bg="#ADD8E6", anchor="e").grid(row=0, column=2, padx=5, pady=4)
        cat_frame = tk.Frame(form, bg="#ADD8E6")
        cat_frame.grid(row=0, column=3, padx=5, pady=4, sticky="w")
        
        # A combobox lets the user pick from the list, but they can't type a new one directly
        self.cat_combo = ttk.Combobox(cat_frame, values=self.categories, textvariable=self.selected_category, state="readonly", width=15, background="#ADD8E6")
        self.cat_combo.pack(side=tk.LEFT)
        
        #  small "+" button opens a dialog to add a new category
        btn_add_cat = tk.Button(cat_frame, text="+", width=2,command=self.add_new_category, bg="#FCFEFF")
        btn_add_cat.pack(side=tk.LEFT, padx=(5, 0))

        # Row 1: amount and date
        tk.Label(form, text="Amount (€):", width=12, bg="#ADD8E6",anchor="e").grid(row=1, column=0, padx=5, pady=4)
        self.amount_entry = tk.Entry(form, width=25)
        self.amount_entry.grid(row=1, column=1, padx=5, pady=4)

        tk.Label(form, text="Date (YYYY-MM-DD):", width=12, bg="#ADD8E6", anchor="e").grid(row=1, column=2, padx=5, pady=4)
        self.date_entry = tk.Entry(form, width=25)
        self.date_entry.insert(0, date.today().isoformat())   # today's date as default
        self.date_entry.grid(row=1, column=3, padx=5, pady=4)

        # Row 2: add transaction button
        tk.Button(form, text="Add Transaction", width=20, command=self.add_transaction).grid(row=2, column=1, columnspan=2, pady=10)

        #  listbox to show all transactions 
        self.listbox = tk.Listbox(root, width=100, height=12, font=("Arial", 9))
        self.listbox.pack(pady=5)

        #  Button frame (Delete, Clear, Summary) 
        btn_frame = tk.Frame(root, bg="#ADD8E6")
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="Delete Selected", width=16, command=self.delete_selected).pack(side=tk.LEFT, padx=6)
        tk.Button(btn_frame, text="Clear All", width=16, command=self.clear_all).pack(side=tk.LEFT, padx=6)
        tk.Button(btn_frame, text="Show Summary", width=16, command=self.show_summary).pack(side=tk.LEFT, padx=6)

        #  Totals and balance display 
        totals_frame = tk.Frame(root, bg="#ADD8E6")
        totals_frame.pack(pady=10)

        self.total_label = tk.Label(totals_frame, text="Total Expenses: €0.00", font=("Arial", 11, "bold"), bg="#ADD8E6")
        self.total_label.grid(row=0, column=0, padx=12)

        self.week_label = tk.Label(totals_frame, text="This Week: €0.00", font=("Arial", 11, "bold"), bg="#ADD8E6")
        self.week_label.grid(row=0, column=1, padx=12)

        self.month_label = tk.Label(totals_frame, text="This Month: €0.00",font=("Arial", 11, "bold"), bg="#ADD8E6")
        self.month_label.grid(row=0, column=2, padx=12)

        self.balance_label = tk.Label(totals_frame, text="Balance: €0.00", font=("Arial", 11, "bold"), bg="#ADD8E6")
        self.balance_label.grid(row=0, column=3, padx=12)

        #  load  saved data and update the UI 
        self.load_transactions()
        self.refresh_listbox()
        self.update_totals()
        self.update_balance()

    # Adding a new category --> a small pop‑up asks for the name
    def add_new_category(self):
        new_cat = simpledialog.askstring("New Category", "Enter category name:", parent=self.root)
        
        # user didn't cancel
        if new_cat:    
            new_cat = new_cat.strip().capitalize()
            if not new_cat:
                messagebox.showwarning("Invalid", "Category name cannot be empty.")
                return
            if new_cat in self.categories:
                messagebox.showinfo("Already exists", f"Category '{new_cat}' already exists.")
                return
            # add to our list
            self.categories.append(new_cat)     
            # update the dropdown
            self.cat_combo['values'] = self.categories   
            # and select it automatically
            self.selected_category.set(new_cat) 
    # Load transactions from the CSV file
    def load_transactions(self):
        self.data = []
        try:
            with open(FILE_NAME, "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) < 5:
                        continue
                    t_type, date_str, desc, cat, amt_str = row
                    try:
                        amount = float(amt_str)
                    except ValueError:
                        continue
                    if t_type and date_str and desc and cat:
                        self.data.append({
                            "type" : t_type,
                            "date" : date_str,
                            "desc" : desc,
                            "category" : cat,
                            "amount" : amount
                        }) 
        except FileNotFoundError:
            # no file
            pass
        except Exception as e:
            messagebox.showerror("Error", f"Could not load tranactions \n{e}")

    # Save all transactions to the CSV file 
    def save_transactions(self):
        try:
            with open(FILE_NAME, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                for t in self.data:
                    writer.writerow([
                        t["type"],
                        t["date"],
                        t["desc"],
                        t["category"],
                        f"{t['amount']:.2f}"
                    ])
        except Exception as e:
            messagebox.showerror("Error", f"Could not save transactionss \n{e}")

    # Refresh the listbox to show the current transactions
    def refresh_listbox(self):
        self.listbox.delete(0, tk.END)
        for i, t in enumerate(self.data, start=1):
            # Put a little [I] or [E] in front so you can easily see income/expense
            icon = "[I]" if t["type"] == "Income" else "[E]"
            line = f"{i}. {icon} {t['date']} | {t['category']} | {t['desc']} | €{t['amount']:.2f}"
            self.listbox.insert(tk.END, line)


    # Calculate the start (Monday) and end (Sunday) of the current week
    def week_start_end(self, today):
        start = today - timedelta(days=today.weekday())  # Monday
        end = start + timedelta(days=6)                  # Sunday
        return start, end

    # Update the three expense totals (all‑time, this week, this month)
    def update_totals(self):
        # Only expenses count towards these totals
        total_expenses = sum(t["amount"] for t in self.data if t["type"] == "Expense")

        today = date.today()
        week_start, week_end = self.week_start_end(today)

        week_expenses = 0.0
        month_expenses = 0.0

        for t in self.data:
            if t["type"] != "Expense":
                continue
            try: 
                d = datetime.strptime(t["date"], "%Y-%m-%d").date()
            except ValueError:
                continue
            if week_start <= d <= week_end:
                week_expenses += t["amount"]
            if d.year == today.year and d.month == today.month:
                month_expenses += t["amount"]
              
        self.total_label.config(text=f"Total Expenses: €{total_expenses:.2f}")
        self.week_label.config(text=f"This Week: €{week_expenses:.2f}")
        self.month_label.config(text=f"This Month: €{month_expenses:.2f}")

    # update the balance (Income – Expense)
    def update_balance(self):
        total_income = sum(t["amount"] for t in self.data if t["type"] == "Income")
        total_expense = sum(t["amount"] for t in self.data if t["type"] == "Expense")
        balance = total_income - total_expense
        self.balance_label.config(text=f"Balance: €{balance:.2f}")

    # Add a new transaction --> (called when the user clicks the button)
    def add_transaction(self):
        t_type = self.trans_type.get()
        desc = self.desc_entry.get().strip()
        cat = self.selected_category.get().strip()
        amount_text = self.amount_entry.get().strip()
        date_text = self.date_entry.get().strip()

        # Validation
        if not desc or not amount_text or not date_text:
            messagebox.showwarning("Missing info", "Please fill in all fields.")
            return

        try:
            amount = float(amount_text)
        except ValueError:
            messagebox.showwarning("Invalid amount", "Amount must be a number.")
            return

        if amount <= 0:
            messagebox.showwarning("Invalid amount", "Amount must be positive.")
            return

        try:
            datetime.strptime(date_text, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Invalid date", "Date must be in YYYY-MM-DD format.")
            return

        if not cat:
            messagebox.showwarning("No category", "Please select a category.")
            return

        # Add the transaction 
        self.data.append({
            "type": t_type,
            "date": date_text,
            "desc": desc,
            "category": cat,
            "amount": amount
        })

        # Clear the input fields --> (keep date as today for convenience)
        self.desc_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, date.today().isoformat())

        # Save everything and update the display
        self.save_transactions()
        self.refresh_listbox()
        self.update_totals()
        self.update_balance()

    # Get the index of the selected item in the listbox
    def get_selected_index(self):
        sel = self.listbox.curselection()
        return sel[0] if sel else None

    # Delete the selected transaction
    def delete_selected(self):
        idx = self.get_selected_index()
        if idx is None:
            messagebox.showinfo("Select something", "Click a transaction first.")
            return

        removed = self.data.pop(idx)
        self.save_transactions()
        self.refresh_listbox()
        self.update_totals()
        self.update_balance()
        messagebox.showinfo("Deleted", f"Removed: {removed['desc']} (€{removed['amount']:.2f})")

    # Delete all transactions --> (after confirmation)
    def clear_all(self):
        if not self.data:
            messagebox.showinfo("Nothing to clear", "No transactions saved.")
            return

        if messagebox.askyesno("Confirm", "Delete ALL transactions?"):
            self.data = []
            self.save_transactions()
            self.refresh_listbox()
            self.update_totals()
            self.update_balance()

    # Show a detailed summary pop‑up (income/expense by category)
    def show_summary(self):
        total_income = 0.0
        total_expense = 0.0
        cat_income = {}
        cat_expense = {}

        for t in self.data:
            amt = t["amount"]
            cat = t["category"]
            if t["type"] == "Income":
                total_income += amt
                cat_income[cat] = cat_income.get(cat, 0) + amt
            else:
                total_expense += amt
                cat_expense[cat] = cat_expense.get(cat, 0) + amt

        if not self.data:
            messagebox.showinfo("Summary", "No transactions yet.")
            return

        # Build a multi‑line string
        summary = f"Total Income:  €{total_income:.2f}\n"
        summary += f"Total Expense: €{total_expense:.2f}\n"
        summary += f"Balance:       €{total_income - total_expense:.2f}\n\n"
        summary += "Income by category:\n"
        for cat, amt in sorted(cat_income.items()):
            summary += f"  {cat}: €{amt:.2f}\n"
        summary += "\nExpense by category:\n"
        for cat, amt in sorted(cat_expense.items()):
            summary += f"  {cat}: €{amt:.2f}\n"

        messagebox.showinfo("Detailed Summary", summary)


#  Start the application 
if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceTracker(root)
    root.mainloop()
