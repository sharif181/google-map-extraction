import os
import tkinter as tk
import tkinter.messagebox as messagebox
from tkinter import ttk

import pandas as pd

from crawler import call_crawler, get_places

# Global variables to store keyword and location
keyword_value = None
location_value = None
tree = None

def notify(message):
    messagebox.showinfo(title="Sucess", message=message)


def call_crawler_helper():
    global keyword_value, location_value, results
    keyword_value = keyword_entry.get()
    location_value = location_entry.get()
    # Pass the keyword and location to the crawler function if needed
    places = get_places(keyword_value, location_value)
    results = call_crawler(places)
    fetch_results()

def remove_selected_row(event):
    # Get the selected item
    selected_item = tree.selection()[0]
    # Remove the selected item from the tree
    tree.delete(selected_item)

def export_to_excel():
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    # Define the path for the folder
    folder_path = os.path.join(desktop_path, "google_map_data")

    # Check if the folder exists, and create it if it doesn't
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder '{folder_path}' created.")
    else:
        print(f"Folder '{folder_path}' already exists.")

    # Extract data from the treeview and store it in a dictionary
    data = {col: [] for col in tree["columns"]}
    for row in tree.get_children():
        values = tree.item(row)["values"]
        for col, value in zip(tree["columns"], values):
            data[col].append(value)
    
    # Convert dictionary to DataFrame and export to Excel
    df = pd.DataFrame(data)
    file_name = f"google_map_data_{keyword_value}_{location_value}.xlsx"
    file_path = os.path.join(folder_path, file_name)
    df.to_excel(file_path, index=False)
    print(f"Data exported to {file_path}")


def fetch_results():
    global results
    try:
        # Get the next result from the generator
        new_result = next(results)
        display_results(new_result)
        # Schedule the next call to fetch_results
        root.after(10000, fetch_results)  # After 10 seconds all the method
    except StopIteration:
        # Generator is exhausted
        print("All results have been fetched.")
        notify(message="All results have been fetched.")

def display_results(new_result=None):
    global tree
    if new_result is None:
        return

    if tree is None:
        columns = list(new_result.keys())
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        for col in columns:
            tree.heading(col, text=col.capitalize(), anchor=tk.CENTER)
            tree.column(col, anchor=tk.CENTER, width=150)

        vert_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        hor_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vert_scrollbar.set, xscrollcommand=hor_scrollbar.set)

        tree.grid(row=0, column=0, sticky='nsew')
        vert_scrollbar.grid(row=0, column=1, sticky='ns')
        hor_scrollbar.grid(row=1, column=0, sticky='ew')

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        tree.bind("<Button-3>", remove_selected_row)

    values = list(new_result.values())
    tree.insert("", tk.END, values=values)

root = tk.Tk()
root.title("Google Map Data Scraper")
root.geometry("800x650")

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

# Export Button
export_button = tk.Button(root, text="Export to Excel", font=('Arial', 12), bg=btn_color, fg="white", command=export_to_excel)
export_button.pack(pady=10)

root.mainloop()
