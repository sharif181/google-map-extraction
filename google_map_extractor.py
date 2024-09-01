import os
import threading
import tkinter as tk
import tkinter.messagebox as messagebox
from datetime import datetime
from tkinter import ttk

import pandas as pd

from crawler import call_crawler, get_places

# Global variables to store keyword and location
keyword_value = None
location_value = None
tree = None
results = []

def notify(message):
    messagebox.showinfo(title="Success", message=message)

def long_running_task_get_places(result_container, keyword_value, location_value):
    places = get_places(keyword_value, location_value)
    result_container["places"] = places

def long_running_task_get_places_by_keyword(result_container, place):
    result = call_crawler(place)
    result_container["place"] = result

def get_place_info(root, result_container):
    if "place" in result_container:
        new_result = result_container["place"]
        display_results(new_result)
        del result_container["place"]

def process_next_place(root, result_container, index):
    if index < len(result_container["places"]):
        place = result_container["places"][index]
        
        # Start a new thread for call_crawler
        thread = threading.Thread(target=long_running_task_get_places_by_keyword, args=(result_container, place))
        thread.start()
        
        # Wait for the thread to finish and then process the result
        root.after(100, lambda: check_thread_completion(root, result_container, thread, index))
    else:
        # All places have been processed
        notify("All places have been processed.")

def check_thread_completion(root, result_container, thread, index):
    if thread.is_alive():
        # If the thread is still running, check again after 100ms
        root.after(100, check_thread_completion, root, result_container, thread, index)
    else:
        # If the thread has finished, process the result and move to the next place
        get_place_info(root, result_container)
        process_next_place(root, result_container, index + 1)

def get_data_places(root, result_container):
    if "places" in result_container:
        # Start processing the first place
        process_next_place(root, result_container, 0)
    else:
        # Keep checking for the "places" key in result_container
        root.after(100, get_data_places, root, result_container)

def call_crawler_helper():
    global keyword_value, location_value
    keyword_value = keyword_entry.get()
    location_value = location_entry.get()

    result_container = {}
    thread = threading.Thread(target=long_running_task_get_places, args=(result_container, keyword_value, location_value))
    thread.start()
    
    # Check for the result of get_places
    get_data_places(root, result_container)

def remove_selected_row(event):
    selected_item = tree.selection()[0]
    tree.delete(selected_item)

def export_to_excel():
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    folder_path = os.path.join(desktop_path, "google_map_data")

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    data = {col: [] for col in tree["columns"]}
    for row in tree.get_children():
        values = tree.item(row)["values"]
        for col, value in zip(tree["columns"], values):
            data[col].append(value)
    
    df = pd.DataFrame(data)
    file_name = f"google_map_data_{keyword_value}_near_{location_value}_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
    file_path = os.path.join(folder_path, file_name)
    df.to_excel(file_path, index=False)
    print(f"Data exported to {file_path}")

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
root.geometry("1040x650")

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
