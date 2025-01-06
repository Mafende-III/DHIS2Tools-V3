import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import requests
import pandas as pd
import os
import json

class DHIS2ImporterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DHIS2 Organization Unit Group Importer")

        # Initialize variables
        self.dhis2_url = ""
        self.username = ""
        self.password = ""
        self.filepath = ""
        
        self.create_ui()

    def create_ui(self):
        # Create the login form
        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack(padx=10, pady=10)

        tk.Label(self.login_frame, text="DHIS2 URL:").grid(row=0, column=0, pady=5)
        self.url_entry = tk.Entry(self.login_frame, width=40)
        self.url_entry.grid(row=0, column=1, pady=5)

        tk.Label(self.login_frame, text="Username:").grid(row=1, column=0, pady=5)
        self.username_entry = tk.Entry(self.login_frame, width=40)
        self.username_entry.grid(row=1, column=1, pady=5)

        tk.Label(self.login_frame, text="Password:").grid(row=2, column=0, pady=5)
        self.password_entry = tk.Entry(self.login_frame, show="*", width=40)
        self.password_entry.grid(row=2, column=1, pady=5)

        self.verify_button = tk.Button(self.login_frame, text="Verify Access", command=self.verify_access)
        self.verify_button.grid(row=3, columnspan=2, pady=10)

    def verify_access(self):
        self.dhis2_url = self.url_entry.get()
        self.username = self.username_entry.get()
        self.password = self.password_entry.get()

        # Check credentials by making a simple API request
        try:
            response = requests.get(f"{self.dhis2_url}/api/me.json", auth=(self.username, self.password))
            if response.status_code == 200:
                messagebox.showinfo("Access Verified", "Credentials Verified Successfully!")
                self.login_frame.pack_forget()  # Hide the login frame
                self.create_import_ui()  # Show the file import UI
            elif response.status_code == 401:
                messagebox.showerror("Error", "Invalid Credentials!")
            else:
                messagebox.showerror("Error", f"Failed to verify access: {response.status_code}")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Connection Error", f"Could not connect to DHIS2 instance: {e}")

    def create_import_ui(self):
        # Create the file selection and import form
        self.import_frame = tk.Frame(self.root)
        self.import_frame.pack(padx=10, pady=10)

        self.template_button = tk.Button(self.import_frame, text="Download Template", command=self.download_template)
        self.template_button.grid(row=0, columnspan=2, pady=10)

        self.file_button = tk.Button(self.import_frame, text="Select CSV File to Import", command=self.select_file)
        self.file_button.grid(row=1, columnspan=2, pady=10)

        self.import_button = tk.Button(self.import_frame, text="Import", command=self.import_file)
        self.import_button.grid(row=2, columnspan=2, pady=10)

        self.report_label = tk.Label(self.import_frame, text="Import Report: Not Started")
        self.report_label.grid(row=3, columnspan=2, pady=10)

        # Add a progress bar for the import process
        self.progress = ttk.Progressbar(self.import_frame, orient="horizontal", length=300, mode="indeterminate")
        self.progress.grid(row=4, columnspan=2, pady=10)

    def download_template(self):
        # Generate a user-friendly template with separate rows for each Organization Unit ID
        template_data = {
            "Organisation Unit Group ID": ["llJtNYUef8Z", "llJtNYUef8Z", "llJtNYUef8Z", "4kGh22NNdVz"],
            "Organisation Unit Group Name": ["Secondary Care", "Secondary Care", "Secondary Care", "Primary Care"],
            "Organisation Unit Group Short Name": ["Secondary", "Secondary", "Secondary", "Primary"],
            "Organisation Unit Group Code": ["SC", "SC", "SC", "PC"],
            "Organisation Unit ID": ["K2Ma05oPvea", "GjwHSnZtIDv", "m5siT5YGdaW", "K2Ma05oPvea"]
        }
        df = pd.DataFrame(template_data)
        template_path = os.path.join(os.getcwd(), 'organization_unit_template.csv')
        df.to_csv(template_path, index=False)
        messagebox.showinfo("Template Downloaded", f"Template downloaded at: {template_path}")

    def select_file(self):
        self.filepath = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if self.filepath:
            messagebox.showinfo("File Selected", f"File selected: {self.filepath}")

    def import_file(self):
        if not self.filepath:
            messagebox.showerror("No File Selected", "Please select a CSV file first.")
            return

        self.progress.start()  # Start the progress bar

        try:
            df = pd.read_csv(self.filepath)
            organisation_unit_groups = {}

            # Initialize counters for updated and ignored items
            updated, ignored = 0, 0

            # Group rows by Organisation Unit Group ID
            for index, row in df.iterrows():
                collection_uid = row['Organisation Unit Group ID']
                name = row['Organisation Unit Group Name']
                short_name = row['Organisation Unit Group Short Name']
                code = row['Organisation Unit Group Code']
                org_unit_id = row['Organisation Unit ID']

                # Create or append the organisation unit group data
                if collection_uid not in organisation_unit_groups:
                    organisation_unit_groups[collection_uid] = {
                        "name": name,
                        "shortName": short_name,
                        "code": code,
                        "organisationUnits": []
                    }

                organisation_unit_groups[collection_uid]["organisationUnits"].append({"id": org_unit_id})

            # Prepare the payload for the API request
            payload = {
                "organisationUnitGroups": [
                    {
                        "id": uid,
                        "name": data["name"],
                        "shortName": data["shortName"],
                        "code": data["code"],
                        "organisationUnits": data["organisationUnits"]
                    }
                    for uid, data in organisation_unit_groups.items()
                ]
            }

            # PATCH to DHIS2 API
            for org_unit_group in payload["organisationUnitGroups"]:
                collection_url = f"{self.dhis2_url}/api/organisationUnitGroups/{org_unit_group['id']}.json"
                response = requests.patch(collection_url, json=org_unit_group, auth=(self.username, self.password))

                if response.status_code == 200:
                    updated += 1
                else:
                    ignored += 1

            # Stop the progress bar and show the result
            self.progress.stop()
            self.report_label.config(
                text=f"Import Report:\nUpdated: {updated}\nIgnored: {ignored}\nTotal: {updated + ignored}"
            )

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during import: {e}")
            self.progress.stop()

if __name__ == "__main__":
    root = tk.Tk()
    app = DHIS2ImporterApp(root)
    root.mainloop()
