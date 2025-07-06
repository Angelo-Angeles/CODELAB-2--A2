import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading

API_KEY = "fca_live_QbnrKPHZ3gINYcipX28gTbUSQImWtezRqvGdF422"
API_BASE = "https://api.freecurrencyapi.com/v1"
HEADERS = {"apikey": API_KEY}

CURRENCIES = {}  # Will store currency code: name

def fetch_all_currencies():
    try:
        res = requests.get(f"{API_BASE}/currencies", headers=HEADERS)
        data = res.json()
        return data.get("data", {})
    except Exception as e:
        messagebox.showerror("Error", f"Could not load currency list.\n{e}")
        return {}

def fetch_rates(base):
    try:
        response = requests.get(f"{API_BASE}/latest", params={"base_currency": base}, headers=HEADERS)
        data = response.json()
        return data.get("data", {})
    except Exception as e:
        messagebox.showerror("API Error", f"Could not fetch exchange rates.\n{e}")
        return {}

def convert():
    amount = amount_entry.get()
    from_cur = from_currency.get()
    to_cur = to_currency.get()

    if not amount or not amount.replace('.', '', 1).isdigit():
        messagebox.showerror("Invalid Input", "Please enter a valid number.")
        return

    rates = fetch_rates(from_cur)
    if to_cur not in rates:
        messagebox.showerror("Conversion Error", f"Cannot convert to {to_cur}")
        return

    rate = rates[to_cur]
    converted = round(float(amount) * rate, 4)
    result_var.set(f"{amount} {from_cur} = {converted} {to_cur}")

def show_help():
    messagebox.showinfo(
        "How to Use",
        "1. Enter the amount of money to convert.\n"
        "2. Select the source currency (From).\n"
        "3. Select the target currency (To).\n"
        "4. Click 'Convert' to get the result.\n\n"
        "Exchange rates are fetched live from the FreeCurrencyAPI."
    )

def show_currency_list():
    win = tk.Toplevel(root)
    win.title("Supported Currencies")
    win.geometry("400x400")
    win.configure(bg="#1c1c1c")

    scrollbar = tk.Scrollbar(win)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    listbox = tk.Listbox(win, bg="#1c1c1c", fg="silver", font=("Segoe UI", 10), yscrollcommand=scrollbar.set)
    for code, info in CURRENCIES.items():
        listbox.insert(tk.END, f"{code} - {info['name']}")
    listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    scrollbar.config(command=listbox.yview)

def populate_currency_dropdowns():
    currency_codes = list(CURRENCIES.keys())
    from_currency["values"] = currency_codes
    to_currency["values"] = currency_codes
    from_currency.set("USD")
    to_currency.set("EUR")

def load_currencies_async():
    def task():
        global CURRENCIES
        CURRENCIES = fetch_all_currencies()
        if CURRENCIES:
            populate_currency_dropdowns()
    threading.Thread(target=task).start()

# GUI setup
root = tk.Tk()
root.title("Currency Converter")
root.geometry("400x360")
root.configure(bg="#1c1c1c")

style = ttk.Style()
style.theme_use("default")
style.configure("TLabel", background="#1c1c1c", foreground="silver", font=("Segoe UI", 10))
style.configure("TButton", background="#d0d0d0", foreground="black", font=("Segoe UI", 10))
style.configure("TCombobox", fieldbackground="#e0e0e0", background="#d0d0d0", foreground="black")
style.configure("TEntry", fieldbackground="#e0e0e0", foreground="black")

# Help Button
help_button = tk.Button(
    root, text="?", command=show_help,
    font=("Segoe UI", 10, "bold"), bg="#444", fg="white", bd=0, width=2, height=1
)
help_button.place(x=5, y=5)

# Title
tk.Label(root, text="Currency Converter", font=("Segoe UI", 14, "bold"), bg="#1c1c1c", fg="silver").pack(pady=(10, 5))

# Input Frame
input_frame = tk.Frame(root, bg="#1c1c1c")
input_frame.pack(pady=10)

tk.Label(input_frame, text="Amount:", font=("Segoe UI", 10)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
amount_entry = ttk.Entry(input_frame, width=15)
amount_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(input_frame, text="From:", font=("Segoe UI", 10)).grid(row=1, column=0, padx=5, pady=5, sticky="e")
from_currency = ttk.Combobox(input_frame, state="readonly", width=12)
from_currency.grid(row=1, column=1, padx=5, pady=5)

tk.Label(input_frame, text="To:", font=("Segoe UI", 10)).grid(row=2, column=0, padx=5, pady=5, sticky="e")
to_currency = ttk.Combobox(input_frame, state="readonly", width=12)
to_currency.grid(row=2, column=1, padx=5, pady=5)

convert_button = ttk.Button(root, text="Convert", command=convert)
convert_button.pack(pady=10)

# Result Label
result_var = tk.StringVar()
result_label = tk.Label(root, textvariable=result_var, font=("Segoe UI", 12), bg="#1c1c1c", fg="white")
result_label.pack(pady=10)

# Show All Currencies Button
view_currencies_btn = ttk.Button(root, text="View All Currencies", command=show_currency_list)
view_currencies_btn.pack(pady=5)

# Load currencies on launch
load_currencies_async()

root.mainloop()