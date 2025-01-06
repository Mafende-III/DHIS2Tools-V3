import requests
import csv
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QComboBox)
from PyQt5.QtGui import QPalette, QColor
import sys

class ProgramRuleExtractorUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Program Rule Extractor")
        self.setGeometry(100, 100, 400, 300)
        self.initUI()

    def initUI(self):
        # Set a light green theme
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#d9f2d9"))
        palette.setColor(QPalette.WindowText, QColor("#000000"))
        self.setPalette(palette)

        layout = QVBoxLayout()

        # Input fields
        self.url_label = QLabel("DHIS2 Base URL:")
        self.url_input = QLineEdit(self)
        layout.addWidget(self.url_label)
        layout.addWidget(self.url_input)

        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit(self)
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)

        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)

        # Program selection
        self.program_label = QLabel("Select Program:")
        self.program_combo = QComboBox(self)
        layout.addWidget(self.program_label)
        layout.addWidget(self.program_combo)

        # Buttons
        self.load_programs_button = QPushButton("Load Programs", self)
        self.load_programs_button.setStyleSheet("background-color: #90ee90; color: #000; font-weight: bold;")
        self.load_programs_button.clicked.connect(self.load_programs)
        layout.addWidget(self.load_programs_button)

        self.extract_button = QPushButton("Extract Program Rules", self)
        self.extract_button.setStyleSheet("background-color: #90ee90; color: #000; font-weight: bold;")
        self.extract_button.clicked.connect(self.extract_program_rules)
        layout.addWidget(self.extract_button)

        self.setLayout(layout)

    def load_programs(self):
        url = self.url_input.text().rstrip('/')  # Remove trailing slash
        username = self.username_input.text()
        password = self.password_input.text()

        try:
            response = requests.get(f"{url}/api/programs?fields=id,displayName", auth=(username, password))
            response.raise_for_status()
            programs = response.json().get("programs", [])

            self.program_combo.clear()
            for program in programs:
                self.program_combo.addItem(program["displayName"], program["id"])

        except requests.exceptions.RequestException as e:
            print(f"Error loading programs: {e}")

    def extract_program_rules(self):
        url = self.url_input.text().rstrip('/')  # Remove trailing slash
        username = self.username_input.text()
        password = self.password_input.text()
        program_uid = self.program_combo.currentData()

        print(f"Fetching program rules for URL: {url}/api/programRules?filter=program:eq:{program_uid}&fields=id,displayName")
        print(f"Program UID: {program_uid}")

        try:
            response = requests.get(
                f"{url}/api/programRules?filter=program:eq:{program_uid}",
                auth=(username, password)
            )
            response.raise_for_status()

            program_rules = response.json().get("programRules", [])

            if not program_rules:
                print(f"No program rules found for Program UID: {program_uid}")
                return

            # Save to CSV
            with open("program_rules.csv", mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Display Name", "ID"])
                for rule in program_rules:
                    writer.writerow([rule["displayName"], rule["id"]])

            print("Program rules successfully exported to program_rules.csv")

        except requests.exceptions.RequestException as e:
            print(f"Error extracting program rules: {e}")


def main():
    app = QApplication(sys.argv)
    extractor_ui = ProgramRuleExtractorUI()
    extractor_ui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
