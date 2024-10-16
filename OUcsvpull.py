import tkinter as tk
from tkinter import messagebox, filedialog
import requests
import pandas as pd
import logging
import time

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Global variable to store level mapping
level_mapping = {}

# Function to authenticate and retrieve organization unit levels
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

# Function to display the levels in a dropdown menu
def display_levels(levels):
    global level_mapping, level_var, level_dropdown
    level_mapping = {level['id']: level['level'] for level in levels if 'id' in level and 'level' in level}

    # Reset the dropdown menu
    level_var.set('')
    menu = level_dropdown['menu']
    menu.delete(0, 'end')

    for level in levels:
        name = level.get('displayName', 'Unknown Level')
        menu.add_command(label=name, command=tk._setit(level_var, level['id']))

    logging.info("Levels successfully loaded into the dropdown menu.")
    # Enable the export button after levels are displayed
    export_button.config(state=tk.NORMAL)

# Function to fetch descendants with retry
def fetch_descendants_with_retry(url, unit_id, auth, retries=3, delay=5):
    for attempt in range(retries):
        try:
            response = requests.get(
                f"{url}/api/organisationUnits/{unit_id}?includeChildren=true&fields=id,name,path,level",
                auth=auth,
                timeout=60
            )
            response.raise_for_status()
            return response.json().get("organisationUnits", [])
        except requests.exceptions.RequestException as e:
            logging.error(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                raise

# Function to export selected organization units and their descendants
def export_ous():
    selected_level_id = level_var.get()

    if not selected_level_id:
        messagebox.showwarning("Warning", "Please select a level to export.")
        logging.warning("No level selected for export.")
        return

    url = url_entry.get().strip()
    username = username_entry.get().strip()
    password = password_entry.get().strip()
    auth = (username, password)

    ous_data = []

    logging.info(f"Exporting organization units starting from level ID: {selected_level_id}")

    try:
        # Fetch the level information for the selected level ID
        level_response = requests.get(f"{url}/api/organisationUnitLevels/{selected_level_id}", auth=auth)
        level_response.raise_for_status()
        level_data = level_response.json()
        level_number = level_data.get('level')
        
        if not level_number:
            raise ValueError("Failed to retrieve level information for the selected level ID.")
        
        logging.info(f"Selected level ID: {selected_level_id}, Level number: {level_number}")

        # Fetch organization units at the selected level
        level_units_response = requests.get(
            f"{url}/api/organisationUnits?level={level_number}&fields=id,name,path,level",
            auth=auth
        )
        level_units_response.raise_for_status()
        level_units_data = level_units_response.json().get("organisationUnits", [])

        for unit in level_units_data:
            unit_id = unit['id']
            logging.info(f"Fetching descendants for organization unit ID: {unit_id}")
            
            # Fetch descendants of the current unit
            descendants_data = fetch_descendants_with_retry(url, unit_id, auth)
            ous_data.extend(descendants_data)

        logging.info(f"Successfully retrieved {len(ous_data)} organization units.")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Failed to retrieve organization units: {e}")
        logging.error(f"Failed to retrieve organization units: {e}")
        return
    except ValueError as e:
        messagebox.showerror("Error", f"{e}")
        logging.error(f"Error: {e}")
        return

    save_ous_to_csv(ous_data)

# Function to save the organization units to a CSV file
def save_ous_to_csv(ous_data):
    if not ous_data:
        messagebox.showinfo("Info", "No organization units retrieved.")
        logging.info("No organization units to save.")
        return

    # Parse the path into separate columns
    max_levels = max([len(ou['path'].split('/')) for ou in ous_data]) - 1
    level_names = [f"Level {i+1}" for i in range(max_levels)]

    data_for_csv = []
    for ou in ous_data:
        path_parts = ou['path'].split('/')[1:]  # Remove the first empty element
        # Pad the list with empty strings if not all levels are present
        path_parts.extend([''] * (max_levels - len(path_parts)))
        data_for_csv.append(path_parts + [ou['id'], ou['name'], ou['level']])

    # Create DataFrame with the columns
    df = pd.DataFrame(data_for_csv, columns=level_names + ['ID', 'Name', 'Level'])

    # Ask the user to select the folder where the CSV will be saved
    folder_selected = filedialog.askdirectory(title="Select Folder to Save CSV")
    
    if not folder_selected:
        messagebox.showwarning("Warning", "No folder selected.")
        logging.warning("No folder selected for saving CSV.")
        return

    # Save the DataFrame to a CSV file
    file_path = f"{folder_selected}/organization_units.csv"
    df.to_csv(file_path, index=False)

    messagebox.showinfo("Success", f"Organization units exported to {file_path}")
    logging.info(f"Organization units successfully exported to {file_path}")

# Setting up the main application window
app = tk.Tk()
app.title("DHIS2 Organization Unit Exporter")
app.geometry("500x400")  # Adjust the window size to better fit the content

# URL input
tk.Label(app, text="DHIS2 URL:").pack(anchor='w')
url_entry = tk.Entry(app, width=50)
url_entry.pack(anchor='w')

# Username input
tk.Label(app, text="Username:").pack(anchor='w')
username_entry = tk.Entry(app, width=50)
username_entry.pack(anchor='w')

# Password input
tk.Label(app, text="Password:").pack(anchor='w')
password_entry = tk.Entry(app, show="*", width=50)
password_entry.pack(anchor='w')

# Verify Button
verify_button = tk.Button(app, text="Verify", command=verify_credentials)
verify_button.pack(pady=10)

# Level Dropdown
level_var = tk.StringVar()
level_dropdown = tk.OptionMenu(app, level_var, ())
level_dropdown.pack(anchor='w', pady=10)

# Export Button
export_button = tk.Button(app, text="Export OUs", state=tk.DISABLED, command=export_ous)
export_button.pack(pady=10)

# Start the application
app.mainloop()
