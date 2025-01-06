import pandas as pd
import json
from tkinter import filedialog, Tk, messagebox

def convert_csv_to_json(csv_file):
    try:
        # Read the CSV file
        df = pd.read_csv(csv_file)

        # Dictionary to hold the grouped data
        organisation_unit_groups = {}

        # Loop through each row in the CSV
        for index, row in df.iterrows():
            collection_uid = row['Organisation Unit Group ID']
            name = row['Organisation Unit Group Name']
            short_name = row['Organisation Unit Group Short Name']
            code = row['Organisation Unit Group Code']
            org_unit_id = row['Organisation Unit ID']

            # If the group doesn't exist yet, create it
            if collection_uid not in organisation_unit_groups:
                organisation_unit_groups[collection_uid] = {
                    "name": name,
                    "shortName": short_name,
                    "code": code,
                    "organisationUnits": []
                }

            # Append the organization unit ID to the group
            organisation_unit_groups[collection_uid]["organisationUnits"].append({"id": org_unit_id})

        # Prepare the final JSON structure
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

        return payload
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while processing the CSV file: {e}")
        return None

def save_json_file(json_data):
    try:
        # Ask user for where to save the JSON file
        root = Tk()
        root.withdraw()  # Hide the Tkinter window
        json_file = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])

        if json_file:
            # Save the JSON data to the selected file
            with open(json_file, 'w') as file:
                json.dump(json_data, file, indent=4)
            messagebox.showinfo("Success", f"JSON file has been saved successfully at {json_file}")
        else:
            messagebox.showwarning("No File Selected", "No file was selected for saving.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while saving the JSON file: {e}")

def main():
    # Ask the user for the CSV file to convert
    root = Tk()
    root.withdraw()  # Hide the Tkinter window
    csv_file = filedialog.askopenfilename(title="Select CSV File", filetypes=[("CSV Files", "*.csv")])

    if csv_file:
        # Convert the CSV to JSON
        json_data = convert_csv_to_json(csv_file)

        if json_data:
            # Save the JSON file
            save_json_file(json_data)
    else:
        messagebox.showwarning("No File Selected", "No CSV file was selected.")

if __name__ == "__main__":
    main()
