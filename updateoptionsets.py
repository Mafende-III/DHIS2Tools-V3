import tkinter as tk
from tkinter import messagebox, ttk
import requests
import logging

# Setup logging
logging.basicConfig(filename="app.log", level=logging.INFO, 
                    format="%(asctime)s - %(levelname)s - %(message)s")

class DHIS2OptionSetUpdater:
    def __init__(self, root):
        self.root = root
        self.root.title("DHIS2 OptionSet Updater")
        self.root.geometry("400x400")
        self.root.configure(bg='#3b5998')  # Blue theme

        # DHIS2 API Credentials
        self.url_label = tk.Label(root, text="DHIS2 URL:", bg='#3b5998', fg='white')
        self.url_label.pack(pady=5)
        self.url_entry = tk.Entry(root, width=40)
        self.url_entry.pack(pady=5)

        self.username_label = tk.Label(root, text="Username:", bg='#3b5998', fg='white')
        self.username_label.pack(pady=5)
        self.username_entry = tk.Entry(root, width=40)
        self.username_entry.pack(pady=5)

        self.password_label = tk.Label(root, text="Password:", bg='#3b5998', fg='white')
        self.password_label.pack(pady=5)
        self.password_entry = tk.Entry(root, width=40, show='*')
        self.password_entry.pack(pady=5)

        self.verify_button = tk.Button(root, text="Verify Access", command=self.verify_access, bg='#1d3557', fg='white')
        self.verify_button.pack(pady=10)

        # OptionSet ID and Value Type fields
        self.optionset_id_label = tk.Label(root, text="OptionSet ID:", bg='#3b5998', fg='white')
        self.optionset_id_label.pack(pady=5)
        self.optionset_id_entry = tk.Entry(root, width=40)
        self.optionset_id_entry.pack(pady=5)

        self.valuetype_label = tk.Label(root, text="Value Type:", bg='#3b5998', fg='white')
        self.valuetype_label.pack(pady=5)

        # Dropdown for Value Types (Initially empty)
        self.valuetype_combobox = ttk.Combobox(root, state="readonly", width=37)
        self.valuetype_combobox.pack(pady=5)

        self.update_button = tk.Button(root, text="Update OptionSet", command=self.update_option_set, bg='#1d3557', fg='white')
        self.update_button.pack(pady=10)

        # Initialize the ValueType field (Fetch if possible, else allow free text)
        self.populate_value_types()

    def verify_access(self):
        """Verify access to DHIS2 instance using provided credentials"""
        url = self.url_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()

        try:
            response = requests.get(url + '/api/system/info', auth=(username, password))
            if response.status_code == 200:
                messagebox.showinfo("Access Verified", "API access verified successfully!")
                logging.info("Access verified successfully.")
            else:
                messagebox.showerror("Error", f"Failed to verify access. Status Code: {response.status_code}")
                logging.error(f"Access verification failed: {response.text}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            logging.error(f"Error during access verification: {str(e)}")

    def populate_value_types(self):
        """Populate Value Types dropdown if possible, else allow free text"""
        url = self.url_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()

        try:
            response = requests.get(url + '/api/optionSets', auth=(username, password))
            if response.status_code == 200:
                # Extract value types from the response (assuming API provides this information)
                value_types = ['TEXT', 'NUMBER', 'BOOLEAN']  # Example static list if API fails
                self.valuetype_combobox['values'] = value_types
            else:
                # Allow free text if API doesn't provide the value types
                self.valuetype_combobox.config(state="normal")
                self.valuetype_combobox.set("Enter Value Type Manually")
        except Exception as e:
            logging.error(f"Error populating value types: {str(e)}")
            self.valuetype_combobox.config(state="normal")
            self.valuetype_combobox.set("Enter Value Type Manually")

    def update_option_set(self):
        """Update OptionSet with new ValueType"""
        url = self.url_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        optionset_id = self.optionset_id_entry.get()
        new_value_type = self.valuetype_combobox.get()

        if not optionset_id or not new_value_type:
            messagebox.showwarning("Input Required", "Please provide both OptionSet ID and Value Type.")
            return

        try:
            # Fetch the current OptionSet data
            fetch_url = f"{url}/api/optionSets/{optionset_id}"
            response = requests.get(fetch_url, auth=(username, password))

            if response.status_code == 200:
                option_set_data = response.json()
                logging.info(f"Fetched OptionSet data: {option_set_data}")
            else:
                messagebox.showerror("Error", f"Failed to retrieve OptionSet. Status Code: {response.status_code}")
                logging.error(f"Failed to retrieve OptionSet {optionset_id}: {response.text}")
                return

            # Update the valueType field in the fetched data
            option_set_data["valueType"] = new_value_type

            # Send the updated data back to the API
            headers = {'Content-Type': 'application/json'}
            update_url = f"{url}/api/optionSets/{optionset_id}"
            response = requests.put(update_url, json=option_set_data, headers=headers, auth=(username, password))

            if response.status_code == 200:
                messagebox.showinfo("Success", "OptionSet updated successfully!")
                logging.info(f"OptionSet {optionset_id} updated successfully.")
            else:
                messagebox.showerror("Error", f"Failed to update OptionSet. Status Code: {response.status_code}")
                logging.error(f"Failed to update OptionSet {optionset_id}: {response.text}")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            logging.error(f"Error during OptionSet update: {str(e)}")

# Initialize the app
if __name__ == "__main__":
    root = tk.Tk()
    app = DHIS2OptionSetUpdater(root)
    root.mainloop()
