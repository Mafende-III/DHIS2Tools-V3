import pandas as pd
import requests
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import base64
from threading import Thread
from openpyxl import Workbook

class DHIS2UserCreator:
    def __init__(self, master):
        self.master = master
        master.title("DHIS2 User Creator")
        
        self.label = tk.Label(master, text="Upload Excel File:")
        self.label.pack()

        self.upload_button = tk.Button(master, text="Browse", command=self.upload_file)
        self.upload_button.pack()

        self.download_button = tk.Button(master, text="Download Template", command=self.download_template)
        self.download_button.pack()

        self.instance_label = tk.Label(master, text="DHIS2 Instance URL:")
        self.instance_label.pack()
        self.instance_entry = tk.Entry(master)
        self.instance_entry.pack()

        self.username_label = tk.Label(master, text="Username:")
        self.username_label.pack()
        self.username_entry = tk.Entry(master)
        self.username_entry.pack()

        self.password_label = tk.Label(master, text="Password:")
        self.password_label.pack()
        self.password_entry = tk.Entry(master, show='*')
        self.password_entry.pack()

        self.start_button = tk.Button(master, text="Start Creation", command=self.start_creation, state=tk.DISABLED)
        self.start_button.pack()

        self.progress_text = scrolledtext.ScrolledText(master, width=50, height=15, state='disabled')
        self.progress_text.pack()

        self.file_path = ""

    def upload_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
        if self.file_path:
            self.start_button.config(state=tk.NORMAL)
            self.progress_text.config(state='normal')
            self.progress_text.insert(tk.END, f"Selected file: {self.file_path}\n")
            self.progress_text.config(state='disabled')

    def download_template(self):
        wb = Workbook()
        ws = wb.active
        ws.title = "User Template"
        
        # Define column headers
        headers = ["Full Name", "Phone Number", "Email Address", "Organisation Unit ID", "User Role ID", "User Group ID"]
        ws.append(headers)

        template_file_path = "DHIS2_User_Template.xlsx"
        wb.save(template_file_path)
        messagebox.showinfo("Download Template", f"Template downloaded as {template_file_path}")

    def start_creation(self):
        thread = Thread(target=self.create_users)
        thread.start()

    def create_users(self):
        self.progress_text.config(state='normal')
        self.progress_text.delete(1.0, tk.END)
        self.progress_text.insert(tk.END, "Starting user creation...\n")
        self.progress_text.config(state='disabled')

        instance_url = self.instance_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()

        data = pd.read_excel(self.file_path)

        for index, row in data.iterrows():
            full_name = row['Full Name']
            phone = self.add_country_code(str(row['Phone Number']))
            email = row['Email Address']
            org_unit_id = row['Organisation Unit ID']
            user_role_id = row['User Role ID']
            user_group_id = row['User Group ID']
            user_password = self.generate_initial_password(full_name)

            first_name, last_name, user_name = self.split_name(full_name)
            response = self.add_user(instance_url, username, password, first_name, last_name, user_name, phone, email, user_password, user_role_id, org_unit_id, user_group_id)

            if response.status_code == 201:
                self.log_progress(f"User {user_name} created successfully.")
            else:
                self.log_progress(f"Failed to create user {user_name}: {response.text}")

        self.log_progress("User creation completed.")

    def add_user(self, instance_url, username, password, first_name, last_name, user_username, phone, email, user_password, user_role_id, org_unit_id, user_group_id):
        url = f'{instance_url}/api/users'
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {base64.b64encode(f'{username}:{password}'.encode()).decode()}"
        }
        data = {
            "firstName": first_name,
            "surname": last_name,
            "username": user_username,
            "phoneNumber": phone,
            "email": email,
            "password": user_password,
            "userRoles": [{"id": user_role_id}],
            "organisationUnits": [{"id": org_unit_id}],
            "userGroups": [{"id": user_group_id}]
        }
        return requests.post(url, headers=headers, json=data)

    def add_country_code(self, phone_number):
        return f"25{phone_number}"

    def generate_initial_password(self, full_name):
        last_name = self.split_name(full_name)[1]
        return f"{last_name}@2023"

    def split_name(self, full_name):
        name_parts = full_name.split(' ')
        if len(name_parts) > 2:
            first_name = ' '.join(name_parts[:-1])
            last_name = name_parts[-1]
        else:
            first_name = name_parts[0]
            last_name = name_parts[1]
        user_name = f"{first_name.lower().replace(' ', '_')}_{last_name.lower()}"
        return first_name, last_name, user_name

    def log_progress(self, message):
        self.progress_text.config(state='normal')
        self.progress_text.insert(tk.END, f"{message}\n")
        self.progress_text.config(state='disabled')
        self.progress_text.yview(tk.END)  # Auto-scroll to the bottom

if __name__ == "__main__":
    root = tk.Tk()
    app = DHIS2UserCreator(root)
    root.mainloop()
