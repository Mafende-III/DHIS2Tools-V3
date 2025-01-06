import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import requests
import pandas as pd
import logging
import time

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Global variable to store level mapping
level_mapping = {}

def verify_credentials():
    url = url_entry.get().strip()
    username = username_entry.get().strip()
    password = password_entry.get().strip()
    auth = (username, password)

    if not url or not username or not password:
        messagebox.showerror("Error", "Please enter all required fields.")
        logging.error("URL, username, or password missing.")
        return

    logging.info(f"Attempting to connect to URL: {url}")

    try:
        response = requests.get(f"{url}/api/organisationUnitLevels", auth=auth)
        response.raise_for_status()
        logging.info("Successfully connected to DHIS2 and retrieved levels.")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Failed to connect: {e}")
        logging.error(f"Connection failed: {e}")
        return

    if response.status_code == 200:
        data = response.json()
        levels = data.get("organisationUnitLevels", [])
        display_levels(levels)
    else:
        messagebox.showerror("Error", "Invalid credentials or URL.")
        logging.error(f"Received unexpected status code {response.status_code}.")

def display_levels(levels):
    global level_mapping
    level_mapping = {level['id']: level['level'] for level in levels if 'id' in level and 'level' in level}

    level_dropdown['values'] = [level.get('displayName', 'Unknown Level') for level in levels]
    level_dropdown.current(0)  # Select the first level by default

    logging.info("Levels successfully loaded into the dropdown menu.")
    export_button.config(state=tk.NORMAL)

def export_selected_level():
    selected_level_name = level_dropdown.get()
    selected_level_id = next((id_ for id_, name in level_mapping.items() if name == selected_level_name), None)

    if not selected_level_id:
        messagebox.showwarning("Warning", "Please select a valid level to export.")
        logging.warning("No valid level selected for export.")
        return

    url = url_entry.get().strip()
    username = username_entry.get().strip()
    password = password_entry.get().strip()
    auth = (username, password)

    logging.info(f"Exporting organization units for selected level ID: {selected_level_id}")

    try:
        response = requests.get(
            f"{url}/api/organisationUnits?level={level_mapping[selected_level_id]}&fields=id,name,code",
            auth=auth
        )
        response.raise_for_status()

        units = response.json().get("organisationUnits", [])
        if not units:
            messagebox.showinfo("Info", "No organization units found for the selected level.")
            logging.info("No organization units found.")
            return

        save_units_to_csv(units)
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Failed to retrieve organization units: {e}")
        logging.error(f"Failed to retrieve organization units: {e}")
        return

def save_units_to_csv(units):
    folder_selected = filedialog.askdirectory(title="Select Folder to Save CSV")

    if not folder_selected:
        messagebox.showwarning("Warning", "No folder selected.")
        logging.warning("No folder selected for saving CSV.")
        return

    df = pd.DataFrame(units)
    file_path = f"{folder_selected}/organization_units.csv"
    df.to_csv(file_path, index=False, columns=['name', 'id', 'code'])

    messagebox.showinfo("Success", f"Organization units exported to {file_path}")
    logging.info(f"Organization units successfully exported to {file_path}")

# Main application setup
app = tk.Tk()
app.title("DHIS2 Organization Unit Exporter")
app.geometry("600x400")

# Add a stylish frame for better visual organization
frame = ttk.Frame(app, padding="10")
frame.pack(fill=tk.BOTH, expand=True)

# Title Label
title_label = ttk.Label(frame, text="DHIS2 Organization Unit Exporter", font=("Helvetica", 16))
title_label.pack(pady=10)

# URL input
tk.Label(frame, text="DHIS2 URL:").pack(anchor='w')
url_entry = ttk.Entry(frame, width=60)
url_entry.pack(anchor='w', pady=5)

# Username input
tk.Label(frame, text="Username:").pack(anchor='w')
username_entry = ttk.Entry(frame, width=60)
username_entry.pack(anchor='w', pady=5)

# Password input
tk.Label(frame, text="Password:").pack(anchor='w')
password_entry = ttk.Entry(frame, show="*", width=60)
password_entry.pack(anchor='w', pady=5)

# Verify Button
verify_button = ttk.Button(frame, text="Verify", command=verify_credentials)
verify_button.pack(pady=10)

# Level Dropdown
level_label = ttk.Label(frame, text="Select Organization Unit Level:")
level_label.pack(anchor='w', pady=5)
level_dropdown = ttk.Combobox(frame, state="readonly", width=57)
level_dropdown.pack(anchor='w', pady=5)

# Export Button
export_button = ttk.Button(frame, text="Export Level", state=tk.DISABLED, command=export_selected_level)
export_button.pack(pady=10)

# Start the application
app.mainloop()
