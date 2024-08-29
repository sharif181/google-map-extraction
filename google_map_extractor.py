import tkinter as tk
from tkinter import ttk

from crawler import call_crawler

# Global variables to store keyword and location
keyword_value = None
location_value = None

def call_crawler_helper():
    global keyword_value, location_value
    keyword_value = keyword_entry.get()
    location_value = location_entry.get()
    # Pass the keyword and location to the crawler function if needed
    results = call_crawler(keyword_value, location_value)
    # Assume results is obtained from call_crawler
    display_results(results)

def display_results(results=None):
    if results is None:
        return
    # Clear previous results
    for widget in table_frame.winfo_children():
        widget.destroy()
    
    # Extract keys and values from the dictionary
    columns = list(results.keys())
    
    # Create Treeview with columns
    tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
    
    # Set up columns and headings
    for col in columns:
        tree.heading(col, text=col.capitalize(), anchor=tk.CENTER)
        tree.column(col, anchor=tk.CENTER, width=100)
    
    # Insert data into the table
    for row in zip(*results.values()):
        tree.insert("", tk.END, values=row)
    
    # Create Scrollbars
    vert_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    hor_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vert_scrollbar.set, xscrollcommand=hor_scrollbar.set)
    
    # Pack the Treeview and Scrollbars
    tree.grid(row=0, column=0, sticky='nsew')
    vert_scrollbar.grid(row=0, column=1, sticky='ns')
    hor_scrollbar.grid(row=1, column=0, sticky='ew')
    
    table_frame.grid_rowconfigure(0, weight=1)
    table_frame.grid_columnconfigure(0, weight=1)

root = tk.Tk()
root.title("Google Map Data Scraper")
root.geometry("600x400")

# Define color scheme
bg_color = "#f0f0f0"
fg_color = "#333333"
btn_color = "#4CAF50"
entry_bg = "#ffffff"

root.configure(bg=bg_color)

# Heading
heading = tk.Label(root, text="Google Map Extractor", font=('Arial', 18, 'bold'), bg=bg_color, fg=fg_color)
heading.pack(pady=10)

# Input Frame
input_frame = tk.Frame(root, bg=bg_color)
input_frame.pack(pady=10)

# Keyword Input
keyword_label = tk.Label(input_frame, text="Keyword:", font=('Arial', 12), bg=bg_color, fg=fg_color)
keyword_label.grid(row=0, column=0, padx=5)
keyword_entry = tk.Entry(input_frame, font=('Arial', 12), width=20, bg=entry_bg, fg=fg_color)
keyword_entry.grid(row=0, column=1, padx=5)

# Location Input
location_label = tk.Label(input_frame, text="Location:", font=('Arial', 12), bg=bg_color, fg=fg_color)
location_label.grid(row=0, column=2, padx=5)
location_entry = tk.Entry(input_frame, font=('Arial', 12), width=20, bg=entry_bg, fg=fg_color)
location_entry.grid(row=0, column=3, padx=5)

# Start Button
start_button = tk.Button(root, text="Start", font=('Arial', 12), bg=btn_color, fg="white", command=call_crawler_helper)
start_button.pack(pady=10)

# Table Frame for Results
table_frame = tk.Frame(root, bg=bg_color)
table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

root.mainloop()
