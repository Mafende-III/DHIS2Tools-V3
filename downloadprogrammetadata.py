import requests
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json

class DHIS2MetadataExporter:
    def __init__(self, master):
        self.master = master
        self.master.title("DHIS2 Metadata Exporter")
        
        # Initialize variables
        self.programs_dict = {}
        self.save_path = ""

        # Create GUI elements
        self.create_widgets()

    def create_widgets(self):
        # URL input
        tk.Label(self.master, text="DHIS2 URL:").grid(row=0, column=0, padx=5, pady=5)
        self.url_entry = tk.Entry(self.master, width=40)
        self.url_entry.grid(row=0, column=1, padx=5, pady=5)

        # Username input
        tk.Label(self.master, text="Username:").grid(row=1, column=0, padx=5, pady=5)
        self.username_entry = tk.Entry(self.master, width=40)
        self.username_entry.grid(row=1, column=1, padx=5, pady=5)

        # Password input
        tk.Label(self.master, text="Password:").grid(row=2, column=0, padx=5, pady=5)
        self.password_entry = tk.Entry(self.master, width=40, show='*')
        self.password_entry.grid(row=2, column=1, padx=5, pady=5)

        # Load programs button
        self.load_button = tk.Button(self.master, text="Load Programs", command=self.load_programs)
        self.load_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Programs selection
        tk.Label(self.master, text="Select Program:").grid(row=4, column=0, padx=5, pady=5)
        self.program_select = ttk.Combobox(self.master, width=37)
        self.program_select.grid(row=4, column=1, padx=5, pady=5)

        # Export button
        self.export_button = tk.Button(self.master, text="Export Metadata", command=self.export_metadata)
        self.export_button.grid(row=5, column=0, columnspan=2, pady=10)

        # Save path button
        self.save_button = tk.Button(self.master, text="Select Save Location", command=self.select_save_location)
        self.save_button.grid(row=6, column=0, columnspan=2, pady=10)

        # Save path display
        self.save_path_label = tk.Label(self.master, text="Save Location: Not Selected")
        self.save_path_label.grid(row=7, column=0, columnspan=2, pady=5)

    def load_programs(self):
        dhis2_url = self.url_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()

        try:
            # Make the API call to get the list of programs
            response = requests.get(f"{dhis2_url}/api/programs.json", auth=(username, password))
            response.raise_for_status()  # Raise an error for bad responses

            # Print the entire response for debugging
            print("Response JSON:", response.json())

            programs = response.json().get('programs', [])
            if not programs:
                messagebox.showwarning("Warning", "No programs found.")
                return

            # Extract program names and IDs
            program_names = []
            program_ids = []
            for program in programs:
                name = program.get('name') or program.get('id') or 'Unnamed Program'
                program_names.append(name)
                program_ids.append(program.get('id', 'No ID Provided'))

            self.programs_dict = dict(zip(program_names, program_ids))

            # Populate the program selection dropdown
            self.program_select['values'] = program_names
            if program_names:
                self.program_select.current(0)  # Select the first program by default

        except requests.exceptions.HTTPError as http_err:
            messagebox.showerror("HTTP Error", f"HTTP error occurred: {http_err}")
        except Exception as err:
            messagebox.showerror("Error", f"An error occurred: {err}")

    def export_metadata(self):
        dhis2_url = self.url_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        selected_program = self.program_select.get()
        program_id = self.programs_dict.get(selected_program)
        
        # Construct the URL for metadata export
        url = f"{dhis2_url}/api/programs/{program_id}/metadata.json"

        try:
            # Make the GET request to export metadata
            response = requests.get(url, auth=(username, password))
            response.raise_for_status()
            
            # Save the metadata to the selected location
            if self.save_path:
                with open(self.save_path, 'w') as json_file:
                    json.dump(response.json(), json_file, indent=4)
                messagebox.showinfo("Success", "Metadata exported successfully!")
            else:
                messagebox.showwarning("Warning", "Please select a save location.")

        except requests.exceptions.HTTPError as http_err:
            messagebox.showerror("HTTP Error", f"HTTP error occurred: {http_err}")
        except Exception as err:
            messagebox.showerror("Error", f"An error occurred: {err}")

    def select_save_location(self):
        self.save_path = filedialog.asksaveasfilename(defaultextension=".json", 
                                                        filetypes=[("JSON files", "*.json"), 
                                                                   ("All files", "*.*")])
        if self.save_path:
            self.save_path_label.config(text=f"Save Location: {self.save_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DHIS2MetadataExporter(root)
    root.mainloop()
