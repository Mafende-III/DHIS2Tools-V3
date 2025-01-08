import csv
import json
import requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLineEdit, QLabel, QVBoxLayout, QWidget,
    QFileDialog, QComboBox, QProgressBar, QMessageBox, QTextEdit
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal


class ImportWorker(QThread):
    progress = pyqtSignal(int)  # Signal to update the progress bar
    error = pyqtSignal(str)     # Signal to show an error message
    success = pyqtSignal()      # Signal when the import is successful

    def __init__(self, url, auth, payload, batch_size):
        super().__init__()
        self.url = url
        self.auth = auth
        self.payload = payload
        self.batch_size = batch_size

    def run(self):
        """Perform the import process in a background thread."""
        total_batches = (len(self.payload) + self.batch_size - 1) // self.batch_size
        for i in range(total_batches):
            batch = self.payload[i * self.batch_size:(i + 1) * self.batch_size]
            payload = {"dataValues": batch}

            try:
                response = requests.post(
                    f"{self.url}/api/dataValueSets",
                    auth=self.auth,
                    json=payload
                )
                response.raise_for_status()
            except requests.RequestException as e:
                self.error.emit(f"Failed to import batch {i + 1}: {str(e)}\nResponse: {response.text}")
                return

            # Emit progress update
            self.progress.emit(i + 1)

        # Emit success signal
        self.success.emit()


class DHIS2Importer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DHIS2 Data Importer")
        self.setGeometry(200, 200, 700, 500)
        self.setStyleSheet("background-color: #e6f7e6;")  # Light green background

        # UI Components
        self.url_label = QLabel("DHIS2 URL:")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter DHIS2 URL")

        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter Username")

        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter Password")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.verify_credentials)

        self.dataset_label = QLabel("Select Dataset:")
        self.dataset_select = QComboBox()
        self.dataset_select.setEnabled(False)

        self.file_button = QPushButton("Select CSV File")
        self.file_button.clicked.connect(self.select_file)
        self.file_button.setEnabled(False)

        self.preview_button = QPushButton("Preview Payload")
        self.preview_button.clicked.connect(self.preview_payload)
        self.preview_button.setEnabled(False)

        self.import_button = QPushButton("Start Import")
        self.import_button.clicked.connect(self.start_import)
        self.import_button.setEnabled(False)

        self.progress_bar = QProgressBar()
        self.payload_preview = QTextEdit()
        self.payload_preview.setReadOnly(True)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.url_label)
        layout.addWidget(self.url_input)
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.dataset_label)
        layout.addWidget(self.dataset_select)
        layout.addWidget(self.file_button)
        layout.addWidget(self.preview_button)
        layout.addWidget(self.import_button)
        layout.addWidget(self.progress_bar)
        layout.addWidget(QLabel("Payload Preview:"))
        layout.addWidget(self.payload_preview)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Variables
        self.csv_file_path = None
        self.dataset_id = None
        self.payload = []
        self.worker = None

    def verify_credentials(self):
        """Verify the provided DHIS2 credentials and fetch datasets."""
        url = self.url_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not url.startswith("http"):
            QMessageBox.warning(self, "Invalid URL", "Please provide a valid DHIS2 URL.")
            return

        try:
            # Make login API call
            response = requests.get(f"{url}/api/me", auth=(username, password))
            response.raise_for_status()

            # Fetch datasets
            datasets_response = requests.get(f"{url}/api/dataSets", auth=(username, password))
            datasets_response.raise_for_status()

            datasets = datasets_response.json()["dataSets"]
            self.dataset_select.clear()
            for dataset in datasets:
                self.dataset_select.addItem(dataset["displayName"], dataset["id"])

            QMessageBox.information(self, "Login Successful", "Credentials verified. Datasets loaded.")
            self.dataset_select.setEnabled(True)
            self.file_button.setEnabled(True)
        except requests.RequestException as e:
            QMessageBox.critical(self, "Login Failed", f"Error: {str(e)}")

    def select_file(self):
        """Open file dialog to select a CSV file."""
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("CSV Files (*.csv)")

        if file_dialog.exec_():
            self.csv_file_path = file_dialog.selectedFiles()[0]
            self.preview_button.setEnabled(True)

    def preview_payload(self):
        """Generate and display JSON payload from the selected CSV file."""
        if not self.csv_file_path:
            QMessageBox.warning(self, "No File", "Please select a CSV file.")
            return

        self.dataset_id = self.dataset_select.currentData()
        if not self.dataset_id:
            QMessageBox.warning(self, "No Dataset", "Please select a dataset.")
            return

        try:
            with open(self.csv_file_path, "r", encoding="utf-8") as csv_file:
                reader = csv.DictReader(csv_file)
                rows = list(reader)

            self.payload = [
                {
                    "dataElement": row["Data Element"].strip(),
                    "period": row["Period"].strip(),
                    "orgUnit": row["Organisation Unit"].strip(),
                    "value": row["Value"].strip()
                }
                for row in rows
                if row["Data Element"].strip() and row["Period"].strip()
                and row["Organisation Unit"].strip() and row["Value"].strip()
            ]

            if not self.payload:
                QMessageBox.warning(self, "Invalid File", "No valid rows found in the CSV file.")
                return

            self.payload_preview.setText(json.dumps({"dataValues": self.payload}, indent=4))
            self.import_button.setEnabled(True)
        except KeyError as e:
            QMessageBox.critical(self, "Error", f"Missing required column: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to process file: {str(e)}")

    def start_import(self):
        """Start importing the JSON payload in batches of 50."""
        if not self.payload:
            QMessageBox.warning(self, "No Payload", "Please generate a payload before importing.")
            return

        url = self.url_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        self.worker = ImportWorker(url, (username, password), self.payload, batch_size=50)
        self.worker.progress.connect(self.update_progress)
        self.worker.error.connect(self.show_error)
        self.worker.success.connect(self.show_success)

        self.progress_bar.setMaximum((len(self.payload) + 49) // 50)
        self.worker.start()

    def update_progress(self, value):
        """Update the progress bar."""
        self.progress_bar.setValue(value)

    def show_error(self, message):
        """Display an error message."""
        QMessageBox.critical(self, "Error", message)

    def show_success(self):
        """Display a success message."""
        QMessageBox.information(self, "Success", "Data imported successfully!")


if __name__ == "__main__":
    app = QApplication([])
    importer = DHIS2Importer()
    importer.show()
    app.exec_()
