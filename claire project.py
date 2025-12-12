import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os, sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # Path used by PyInstaller
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ----- Import matplotlib for graphs -----
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ----- Global storage -----
daily_data = []  # Listahan ng bawat araw na may tuple: (date, sales, expenses, net)
JSON_FILE = "sales_data.json"

# ----- Main Window -----
root = tk.Tk()
root.title("📊 Daily and Monthly Sales Tracker")  # Pamagat ng window
root.geometry("750x650")  # Laki ng window
root.state("zoomed")          # Auto-maximize pag bukas
root.resizable(True, True)    # Pwede na i-resize
root.iconbitmap(resource_path("sale.ico"))

# ----- Style -----
style = ttk.Style()
style.theme_use("clam")  # Tema para sa widgets
style.configure("TButton", font=('Arial', 10, 'bold'), foreground="#FFFFFF")  # Button style
style.map("TButton", background=[('active', '#4B4B4B')])  # Kulay kapag naka-hover/click
style.configure("TLabel", font=('Arial', 11), background="#FFF8E7", foreground="#000000")  # Label style
style.configure("TEntry", font=('Arial', 11))  # Entry (input) style

# ----- Header / Banner -----
header = tk.Frame(root, bg="#4B4B4B", height=60)  # Dark grey na header
header.pack(fill="x")  # Full width
header_label = tk.Label(header, text="📊 Daily and Monthly Sales Tracker", bg="#4B4B4B", fg="#FFFFFF", font=("Arial", 18, "bold"))
header_label.pack(pady=10)

# ----- Input Frame -----
input_frame = tk.Frame(root, bg="#FFF8E7")
input_frame.pack(pady=15)

# Label at Entry para sa Date
tk.Label(input_frame, text="Date (YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
date_entry = tk.Entry(input_frame, font=("Arial", 12))
date_entry.grid(row=0, column=1, padx=5, pady=5)
date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))  # Default na petsa: today

# Label at Entry para sa Sales
tk.Label(input_frame, text="Today's Sales (₱):").grid(row=1, column=0, padx=5, pady=5, sticky="e")
sales_entry = tk.Entry(input_frame, font=("Arial", 12))
sales_entry.grid(row=1, column=1, padx=5, pady=5)

# Label at Entry para sa Expenses
tk.Label(input_frame, text="Today's Expenses (₱):").grid(row=2, column=0, padx=5, pady=5, sticky="e")
expenses_entry = tk.Entry(input_frame, font=("Arial", 12))
expenses_entry.grid(row=2, column=1, padx=5, pady=5)

# Feedback label para sa user
feedback_label = tk.Label(root, text="", font=("Arial", 11), fg="#2E7D32", bg="#FFF8E7")  # Dark green
feedback_label.pack(pady=5)

# ----- Table Frame -----
table_frame = tk.Frame(root, bg="#FFF8E7")
table_frame.pack(pady=10)

# Treeview table para sa daily records
columns = ("Date", "Sales", "Expenses", "Net")
tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor="center", width=150)

# Striped rows para sa table
tree.tag_configure('oddrow', background="#EDEDED", foreground="#000000")  # Light grey
tree.tag_configure('evenrow', background="#FFFFFF", foreground="#000000")  # White
tree.pack()

# ----- Progress Bar -----
progress = ttk.Progressbar(root, orient="horizontal", length=500, mode="determinate")  # Progress bar
progress.pack(pady=10)

# ----- Functions -----

# SAVE & LOAD FUNCTIONS (JSON version)
def save_to_file():
    """Save daily_data to a JSON file"""
    data_to_save = [
        {"date": entry[0], "sales": entry[1], "expenses": entry[2], "net": entry[3]}
        for entry in daily_data
    ]
    try:
        with open(JSON_FILE, "w", encoding="utf-8") as file:
            json.dump(data_to_save, file, indent=4)
        feedback_label.config(text="💾 Data saved successfully!")
    except Exception as e:
        messagebox.showerror("Save Error", f"Failed to save data: {e}")

def load_from_file():
    """Load daily_data from a JSON file"""
    if not os.path.exists(JSON_FILE):
        return

    try:
        with open(JSON_FILE, "r", encoding="utf-8") as file:
            loaded_data = json.load(file)
        for entry in loaded_data:
            date = entry["date"]
            sales = float(entry["sales"])
            expenses = float(entry["expenses"])
            net = float(entry["net"])
            daily_data.append((date, sales, expenses, net))

            tag = 'evenrow' if len(tree.get_children()) % 2 == 0 else 'oddrow'
            tree.insert("", tk.END,
                        values=(date, f"₱{sales:,.2f}", f"₱{expenses:,.2f}", f"₱{net:,.2f}"),
                        tags=(tag,))
    except Exception as e:
        messagebox.showerror("Load Error", f"Failed to load data: {e}")

# Function para mag-add ng entry
def add_entry():
    date_str = date_entry.get().strip()
    try:
        datetime.strptime(date_str, "%Y-%m-%d")  # Check valid date
    except ValueError:
        messagebox.showerror("Invalid Date", "Enter a valid date (YYYY-MM-DD).")
        return

    try:
        sales = float(sales_entry.get())  # Convert sales to float
        expenses = float(expenses_entry.get())  # Convert expenses to float
    except ValueError:
        messagebox.showerror("Invalid Input", "Enter valid numbers.")
        return

    net = sales - expenses  # Calculate net
    daily_data.append((date_str, sales, expenses, net))  # Add sa list

    # Insert sa Treeview
    tag = 'evenrow' if len(tree.get_children()) % 2 == 0 else 'oddrow'
    tree.insert("", tk.END, values=(date_str, f"₱{sales:,.2f}", f"₱{expenses:,.2f}", f"₱{net:,.2f}"), tags=(tag,))
    feedback_label.config(text=f"✅ Added entry for {date_str} | Net: ₱{net:,.2f}")
    
    save_to_file()  # Auto save

    # Clear entries
    sales_entry.delete(0, tk.END)
    expenses_entry.delete(0, tk.END)

# Function para mag-delete ng selected entry
def delete_selected():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("No Selection", "Select an entry to delete.")
        return

    confirm = messagebox.askyesno("Confirm Delete", "Are you sure?")
    if confirm:
        item = selected_item[0]
        values = tree.item(item, "values")
        date, sales_str, expenses_str, net_str = values

        # Convert string to float
        sales_val = float(sales_str.replace("₱", "").replace(",", ""))
        expenses_val = float(expenses_str.replace("₱", "").replace(",", ""))
        net_val = float(net_str.replace("₱", "").replace(",", ""))
        
        # Remove sa daily_data list
        for entry in daily_data:
            if entry == (date, sales_val, expenses_val, net_val):
                daily_data.remove(entry)
                break

        # Remove sa treeview
        tree.delete(item)
        feedback_label.config(text=f"🗑️ Deleted entry for {date}")
        save_to_file()  # Auto save

# Function para mag-show ng monthly report
def show_monthly_report():
    if not daily_data:
        messagebox.showinfo("No Data", "No entries recorded yet.")
        return

    total_sales = sum(x[1] for x in daily_data)
    total_expenses = sum(x[2] for x in daily_data)
    net_sales = total_sales - total_expenses
    ten_percent = net_sales * 0.10

    # Animate progress bar
    progress["value"] = 0
    for i in range(0, 101, 10):
        progress["value"] = i
        root.update()
        root.after(30)

    # New window for report
    report_win = tk.Toplevel(root)
    report_win.title("📊 Monthly Sales Report")
    report_win.state("zoomed")
    report_win.resizable(True, True)
    report_win.iconbitmap(resource_path("sale.ico"))

    report_win.configure(bg="#FFF8E7")  # Cream

    # Title
    tk.Label(report_win, text="📅 Monthly Sales Report", font=("Arial", 16, "bold"), bg="#FFF8E7", fg="#000000").pack(pady=10)

    # Separator line
    separator = tk.Frame(report_win, height=2, bd=1, relief="sunken", bg="#4B4B4B")
    separator.pack(fill="x", padx=20, pady=5)

    report_content = tk.Frame(report_win, bg="#FFF8E7")
    report_content.pack(pady=10, padx=10, fill="x")

   
    # Summary frame ng totals
    summary_frame = tk.Frame(report_content, bg="#FFF8E7")
    summary_frame.pack(side="left", padx=10)

    labels = ["Total Sales:", "Total Expenses:", "Net Sales:", "10% of Net Sales:"]
    values = [f"₱{total_sales:,.2f}", f"₱{total_expenses:,.2f}", f"₱{net_sales:,.2f}", f"₱{ten_percent:,.2f}"]

    for i in range(len(labels)):
        tk.Label(summary_frame, text=labels[i], font=("Arial", 12, "bold"), anchor="w", bg="#FFF8E7", fg="#000000").grid(row=i, column=0, sticky="w", padx=20, pady=5)
        tk.Label(summary_frame, text=values[i], font=("Arial", 12), anchor="e", bg="#FFF8E7", fg="#000000").grid(row=i, column=1, sticky="e", padx=20, pady=5)

    # Daily Records Table sa report
    tk.Label(report_win, text="📝 Daily Records:", font=("Arial", 12, "bold"), bg="#FFF8E7", fg="#000000").pack(pady=10)
    daily_frame = tk.Frame(report_win, bg="#FFF8E7")
    daily_frame.pack()

    daily_tree = ttk.Treeview(daily_frame, columns=("Date", "Sales", "Expenses", "Net"), show="headings", height=8)
    for col in ("Date", "Sales", "Expenses", "Net"):
        daily_tree.heading(col, text=col)
        daily_tree.column(col, width=90, anchor="center")

    for i, entry in enumerate(daily_data):
        date, sales, expenses, net = entry
        tag = 'evenrow' if i % 2 == 0 else 'oddrow'
        daily_tree.insert("", tk.END, values=(date, f"₱{sales:,.2f}", f"₱{expenses:,.2f}", f"₱{net:,.2f}"), tags=(tag,))
    daily_tree.tag_configure('oddrow', background="#EDEDED", foreground="#000000")
    daily_tree.tag_configure('evenrow', background="#FFFFFF", foreground="#000000")
    daily_tree.pack(padx=10, pady=5)

    # Close button
    tk.Button(report_win, text="Close", command=report_win.destroy, bg="#A0A0A0", fg="#FFFFFF", font=("Arial", 11, "bold"), width=15).pack(pady=10)

# ----- Analytics Function with Graphs -----
def show_analytics():
    if not daily_data:
        messagebox.showinfo("No Data", "No entries recorded yet.")
        return

    total_sales = sum(x[1] for x in daily_data)
    total_expenses = sum(x[2] for x in daily_data)
    total_net = sum(x[3] for x in daily_data)
    average_sales = total_sales / len(daily_data)
    average_expenses = total_expenses / len(daily_data)
    highest_net = max(daily_data, key=lambda x: x[3])
    lowest_net = min(daily_data, key=lambda x: x[3])

    # Analytics window
    analytics_win = tk.Toplevel(root)
    analytics_win.title("📈 Sales Analytics")
    analytics_win.state("zoomed")
    analytics_win.resizable(True, True)
    analytics_win.configure(bg="#FFF8E7")
    analytics_win.iconbitmap(resource_path("sale.ico"))

    tk.Label(analytics_win, text="📈 Sales Analytics", font=("Arial", 16, "bold"), bg="#FFF8E7", fg="#000000").pack(pady=10)

    # Separator
    separator = tk.Frame(analytics_win, height=2, bd=1, relief="sunken", bg="#4B4B4B")
    separator.pack(fill="x", padx=20, pady=5)

    # Text summary frame
    analytics_frame = tk.Frame(analytics_win, bg="#FFF8E7")
    analytics_frame.pack(side="left", padx=10, pady=10, fill="y")

    labels = [
        "Total Sales:",
        "Total Expenses:",
        "Total Net:",
        "Average Daily Sales:",
        "Average Daily Expenses:",
        "Highest Net (Date):",
        "Lowest Net (Date):"
    ]

    values = [
        f"₱{total_sales:,.2f}",
        f"₱{total_expenses:,.2f}",
        f"₱{total_net:,.2f}",
        f"₱{average_sales:,.2f}",
        f"₱{average_expenses:,.2f}",
        f"{highest_net[0]} → ₱{highest_net[3]:,.2f}",
        f"{lowest_net[0]} → ₱{lowest_net[3]:,.2f}"
    ]

    for i in range(len(labels)):
        tk.Label(analytics_frame, text=labels[i], font=("Arial", 12, "bold"), anchor="w", bg="#FFF8E7", fg="#000000").grid(row=i, column=0, sticky="w", padx=10, pady=5)
        tk.Label(analytics_frame, text=values[i], font=("Arial", 12), anchor="e", bg="#FFF8E7", fg="#000000").grid(row=i, column=1, sticky="e", padx=10, pady=5)

    # ----- Matplotlib Graph -----
    graph_frame = tk.Frame(analytics_win, bg="#FFF8E7")
    graph_frame.pack(side="right", padx=10, pady=10)

    dates = [x[0] for x in daily_data]
    sales_list = [x[1] for x in daily_data]
    expenses_list = [x[2] for x in daily_data]
    net_list = [x[3] for x in daily_data]

    fig, ax = plt.subplots(figsize=(10,6))
    ax.plot(dates, sales_list, marker='o', label="Sales", color='green')
    ax.plot(dates, expenses_list, marker='o', label="Expenses", color='red')
    ax.plot(dates, net_list, marker='o', label="Net", color='blue')
    ax.set_xlabel("Date")
    ax.set_ylabel("₱ Amount")
    ax.set_title("Daily Sales Overview")
    ax.legend()
    ax.grid(True)
    plt.xticks(rotation=45)

    canvas = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

    tk.Button(analytics_win, text="Close", command=analytics_win.destroy, bg="#A0A0A0", fg="#FFFFFF", font=("Arial", 11, "bold"), width=15).pack(pady=10, side="bottom")

# ----- Buttons sa main window -----
btn_frame = tk.Frame(root, bg="#FFF8E7")
btn_frame.pack(pady=15)

btn_add = tk.Button(btn_frame, text="➕ Add Entry", command=add_entry, bg="#A0A0A0", fg="#FFFFFF", font=("Arial", 10, "bold"), width=18)
btn_add.grid(row=0, column=0, padx=10)

btn_delete = tk.Button(btn_frame, text="🗑️ Delete Entry", command=delete_selected, bg="#A0A0A0", fg="#FFFFFF", font=("Arial", 10, "bold"), width=18)
btn_delete.grid(row=0, column=1, padx=10)

btn_report = tk.Button(btn_frame, text="📊 Monthly Report", command=show_monthly_report, bg="#A0A0A0", fg="#FFFFFF", font=("Arial", 10, "bold"), width=18)
btn_report.grid(row=0, column=2, padx=10)

btn_save = tk.Button(btn_frame, text="💾 Save Data", command=save_to_file, bg="#A0A0A0", fg="#FFFFFF", font=("Arial", 10, "bold"), width=18)
btn_save.grid(row=1, column=1, pady=10)

btn_analytics = tk.Button(btn_frame, text="📈 Analytics", command=show_analytics, bg="#A0A0A0", fg="#FFFFFF", font=("Arial", 10, "bold"), width=18)
btn_analytics.grid(row=1, column=2, pady=10)

# ----- Load data kapag start -----
load_from_file()

# Run main loop
root.mainloop()