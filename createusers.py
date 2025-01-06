import pandas as pd
import requests
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import base64
import smtplib
from email.mime.text import MIMEText
from threading import Thread
from openpyxl import Workbook
import re

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

        self.email_sender_label = tk.Label(master, text="Email Sender Address:")
        self.email_sender_label.pack()
        self.email_sender_entry = tk.Entry(master)
        self.email_sender_entry.pack()

        self.email_password_label = tk.Label(master, text="Email Sender Password:")
        self.email_password_label.pack()
        self.email_sender_password_entry = tk.Entry(master, show='*')
        self.email_sender_password_entry.pack()

        self.start_button = tk.Button(master, text="Start Creation", command=self.start_creation, state=tk.DISABLED)
        self.start_button.pack()

        self.export_button = tk.Button(master, text="Export Imported Details", command=self.export_details, state=tk.DISABLED)
        self.export_button.pack()

        self.progress_text = scrolledtext.ScrolledText(master, width=70, height=20, state='disabled')
        self.progress_text.pack()

        self.file_path = ""
        self.created_or_updated_users = []  # Successful user creation or update
        self.failed_users = []  # Failed user creation or update

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
        
        headers = [
            "Full Name", "Phone Number", "Email Address",
            "Organisation Unit ID", "User Role ID", "User Group ID",
            "dataViewOrganisationUnits", "teiSearchOrganisationUnits"
        ]
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
        email_sender = self.email_sender_entry.get()
        email_sender_password = self.email_sender_password_entry.get()

        data = pd.read_excel(self.file_path).fillna("")
        self.created_or_updated_users.clear()
        self.failed_users.clear()

        for _, row in data.iterrows():
            full_name = row['Full Name']
            phone = self.add_country_code(str(row['Phone Number']))
            email = self.validate_email(row['Email Address'])
            if not email:
                self.log_progress(f"Invalid email for user {full_name}. Skipping.\n")
                self.failed_users.append({**row, "Status": "Failed - Invalid Email"})
                continue

            org_unit_id = row['Organisation Unit ID']
            user_role_id = row['User Role ID']
            user_group_id = row['User Group ID']
            data_view_ou = row['dataViewOrganisationUnits']
            tei_search_ou = row['teiSearchOrganisationUnits']
            user_password = self.generate_initial_password(full_name)

            first_name, last_name, user_name = self.split_name(full_name)

            user_id = self.get_existing_user_id(instance_url, username, password, user_name)

            if user_id:
                if self.user_details_match(instance_url, username, password, user_id, first_name, last_name, phone, email, user_role_id, org_unit_id, user_group_id, data_view_ou, tei_search_ou):
                    self.log_progress(f"No changes for user {user_name}. Skipping update.\n")
                else:
                    self.log_progress(f"User {user_name} exists but requires updates.\n")
                    if self.update_user(instance_url, username, password, user_id, first_name, last_name, phone, email, user_role_id, org_unit_id, user_group_id, data_view_ou, tei_search_ou):
                        self.log_progress(f"User {user_name} updated successfully.\n")
                        self.created_or_updated_users.append({
                            **row, "Username": user_name, "Password": user_password, "Status": "Updated"
                        })
                    else:
                        self.log_progress(f"Failed to update user {user_name}.\n")
                        self.failed_users.append({**row, "Status": "Failed - Update Error"})
            else:
                response, payload = self.add_user(
                    instance_url, username, password,
                    first_name, last_name, user_name, phone, email,
                    user_password, user_role_id, org_unit_id,
                    user_group_id, data_view_ou, tei_search_ou
                )
                if response.status_code == 201:
                    self.log_progress(f"User {user_name} created successfully.\n")
                    self.send_email(email_sender, email_sender_password, email, full_name, user_password)
                    self.created_or_updated_users.append({
                        **row, "Username": user_name, "Password": user_password, "Status": "Created"
                    })
                else:
                    self.log_progress(f"Failed to create user {user_name}.\n")
                    self.failed_users.append({**row, "Status": "Failed - Creation Error"})

        self.log_progress("User creation completed.\n")
        if self.created_or_updated_users or self.failed_users:
            self.export_button.config(state=tk.NORMAL)

    def validate_email(self, email):
        emails = [e.strip() for e in email.split(",")]
        for e in emails:
            if re.match(r"[^@]+@[^@]+\.[^@]+", e):
                return e
        return None

    def get_existing_user_id(self, instance_url, username, password, user_name):
        url = f"{instance_url}/api/users?filter=username:eq:{user_name}"
        headers = {
            "Authorization": f"Basic {base64.b64encode(f'{username}:{password}'.encode()).decode()}"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            users = response.json().get("users")
            if users:
                return users[0]["id"]
        return None

    def user_details_match(self, instance_url, username, password, user_id, first_name, last_name, phone, email, user_role_id, org_unit_id, user_group_id, data_view_ou, tei_search_ou):
        url = f"{instance_url}/api/users/{user_id}"
        headers = {
            "Authorization": f"Basic {base64.b64encode(f'{username}:{password}'.encode()).decode()}"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            return (
                user_data["firstName"] == first_name and
                user_data["surname"] == last_name and
                user_data["phoneNumber"] == phone and
                user_data["email"] == email and
                user_data["userRoles"][0]["id"] == user_role_id and
                user_data["organisationUnits"][0]["id"] == org_unit_id and
                user_data["userGroups"][0]["id"] == user_group_id and
                user_data["dataViewOrganisationUnits"][0]["id"] == data_view_ou and
                user_data["teiSearchOrganisationUnits"][0]["id"] == tei_search_ou
            )
        return False

    def update_user(self, instance_url, username, password, user_id, first_name, last_name, phone, email, user_role_id, org_unit_id, user_group_id, data_view_ou, tei_search_ou):
        url = f"{instance_url}/api/users/{user_id}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {base64.b64encode(f'{username}:{password}'.encode()).decode()}"
        }
        data = {
            "firstName": first_name,
            "surname": last_name,
            "phoneNumber": phone,
            "email": email,
            "userRoles": [{"id": user_role_id}],
            "organisationUnits": [{"id": org_unit_id}],
            "userGroups": [{"id": user_group_id}],
            "dataViewOrganisationUnits": [{"id": data_view_ou}],
            "teiSearchOrganisationUnits": [{"id": tei_search_ou}]
        }
        response = requests.put(url, headers=headers, json=data)
        return response.status_code == 200

    def add_user(self, instance_url, username, password, first_name, last_name, user_username, phone, email, user_password, user_role_id, org_unit_id, user_group_id, data_view_ou, tei_search_ou):
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
            "userGroups": [{"id": user_group_id}],
            "dataViewOrganisationUnits": [{"id": data_view_ou}],
            "teiSearchOrganisationUnits": [{"id": tei_search_ou}]
        }
        response = requests.post(url, headers=headers, json=data)
        return response, data

    def send_email(self, sender_email, sender_password, recipient_email, full_name, password):
        subject = "Your Account has been Created"
        body = f"Hello {full_name},\n\nYour account has been created successfully.\nUsername: {recipient_email}\nPassword: {password}\n\nPlease log in to the system and change your password as soon as possible."
        
        try:
            smtp_server = "mail.hisprwanda.org"
            smtp_port = 465

            with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                server.login(sender_email, sender_password)
                msg = MIMEText(body)
                msg["Subject"] = subject
                msg["From"] = sender_email
                msg["To"] = recipient_email
                server.sendmail(sender_email, recipient_email, msg.as_string())
                self.log_progress(f"Email sent to {recipient_email}.")
        except Exception as e:
            self.log_progress(f"Failed to send email to {recipient_email}: {str(e)}")

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

    def export_details(self):
        if not self.created_or_updated_users and not self.failed_users:
            messagebox.showwarning("Export Warning", "No users to export.")
            return

        with pd.ExcelWriter(filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])) as writer:
            if self.created_or_updated_users:
                pd.DataFrame(self.created_or_updated_users).to_excel(writer, index=False, sheet_name="Created_Updated_Users")
            if self.failed_users:
                pd.DataFrame(self.failed_users).to_excel(writer, index=False, sheet_name="Failed_Users")
            messagebox.showinfo("Export Successful", "User details exported successfully.")

    def log_progress(self, message):
        self.progress_text.config(state='normal')
        self.progress_text.insert(tk.END, f"{message}\n")
        self.progress_text.config(state='disabled')
        self.progress_text.yview(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = DHIS2UserCreator(root)
    root.mainloop()
