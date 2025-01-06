import sys
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QComboBox, QPushButton, QLabel, \
    QTableWidget, QTableWidgetItem, QHeaderView, QFormLayout, QMessageBox, QRadioButton, QCheckBox, QStackedWidget
from PyQt5.QtCore import Qt

# Constants
PRIMARY_COLOR = "#89CFF0"
TEXT_COLOR = "black"  # Font color for readability


class DHIS2App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DHIS2 Data Exporter")
        self.setGeometry(100, 100, 800, 600)

        # Create the stacked widget for pages
        self.stacked_widget = QStackedWidget(self)
        self.setCentralWidget(self.stacked_widget)

        # Initialize data variables
        self.program_indicators = []
        self.selected_indicators = []
        self.org_unit_id = None
        self.period_type = None
        self.selected_program_group = None
        self.current_indicator_index = 0  # To track the current program indicator being processed

        # Page 1: Login and Credentials
        self.login_page = QWidget(self)
        self.login_layout = QVBoxLayout(self.login_page)

        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText("Enter DHIS2 URL")
        self.url_input.setStyleSheet(f"background-color: {PRIMARY_COLOR}; color: {TEXT_COLOR}; border-radius: 5px; padding: 10px;")

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Enter Username")
        self.username_input.setStyleSheet(f"background-color: {PRIMARY_COLOR}; color: {TEXT_COLOR}; border-radius: 5px; padding: 10px;")

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Enter Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(f"background-color: {PRIMARY_COLOR}; color: {TEXT_COLOR}; border-radius: 5px; padding: 10px;")

        self.verify_button = QPushButton('Verify Access', self)
        self.verify_button.setStyleSheet(f"background-color: {PRIMARY_COLOR}; color: white; border-radius: 5px; padding: 10px;")
        self.verify_button.clicked.connect(self.verify_access)

        self.login_layout.addWidget(self.url_input)
        self.login_layout.addWidget(self.username_input)
        self.login_layout.addWidget(self.password_input)
        self.login_layout.addWidget(self.verify_button)

        self.stacked_widget.addWidget(self.login_page)

    def verify_access(self):
        """Verify DHIS2 access and fetch program indicator groups"""
        url = self.url_input.text()
        username = self.username_input.text()
        password = self.password_input.text()

        try:
            response = requests.get(f"{url}/api/programIndicatorGroups", auth=(username, password))
            response.raise_for_status()
            program_groups = response.json()['programIndicatorGroups']
            self.populate_program_groups(program_groups)
            self.stacked_widget.setCurrentIndex(1)  # Go to program group selection page
        except requests.exceptions.RequestException as e:
            self.show_error(f"Failed to connect to DHIS2 instance: {e}")

    def populate_program_groups(self, program_groups):
        """Populate program indicator groups dropdown with available groups"""
        self.program_group_select = QComboBox(self)
        self.program_group_select.clear()

        for group in program_groups:
            group_name = group.get('displayName', 'Unnamed Group')
            group_id = group.get('id', 'No ID')
            self.program_group_select.addItem(group_name, group_id)

        self.program_group_select.currentIndexChanged.connect(self.load_program_indicators_step)

        program_group_layout = QVBoxLayout()
        program_group_layout.addWidget(QLabel("Select Program Group"))
        program_group_layout.addWidget(self.program_group_select)

        next_button = QPushButton('Next', self)
        next_button.clicked.connect(self.load_program_indicators_step)
        program_group_layout.addWidget(next_button)

        program_group_page = QWidget(self)
        program_group_page.setLayout(program_group_layout)

        self.stacked_widget.addWidget(program_group_page)

    def load_program_indicators_step(self):
        """Load program indicators for the selected program indicator group"""
        group_id = self.program_group_select.currentData()
        self.selected_program_group = group_id
        url = self.url_input.text()
        username = self.username_input.text()
        password = self.password_input.text()

        try:
            response = requests.get(f"{url}/api/programIndicators?programIndicatorGroup={group_id}", auth=(username, password))
            response.raise_for_status()
            self.program_indicators = response.json()['programIndicators']
            self.populate_program_indicators_table()
            self.stacked_widget.setCurrentIndex(2)  # Move to program indicator selection page
        except requests.exceptions.RequestException as e:
            self.show_error(f"Failed to load program indicators: {e}")

    def populate_program_indicators_table(self):
        """Populate the table with program indicators"""
        self.program_indicators_table = QTableWidget(self)
        self.program_indicators_table.setRowCount(len(self.program_indicators))
        self.program_indicators_table.setColumnCount(3)
        self.program_indicators_table.setHorizontalHeaderLabels(['ID', 'Name', 'Select'])

        for i, indicator in enumerate(self.program_indicators):
            self.program_indicators_table.setItem(i, 0, QTableWidgetItem(indicator['id']))
            self.program_indicators_table.setItem(i, 1, QTableWidgetItem(indicator['displayName']))
            radio_button = QCheckBox(self)
            self.program_indicators_table.setCellWidget(i, 2, radio_button)

        self.select_all_radio_button = QRadioButton("Select All", self)
        self.select_all_radio_button.clicked.connect(self.select_all_program_indicators)

        program_indicator_layout = QVBoxLayout()
        program_indicator_layout.addWidget(QLabel("Select Program Indicators"))
        program_indicator_layout.addWidget(self.program_indicators_table)
        program_indicator_layout.addWidget(self.select_all_radio_button)

        next_button = QPushButton('Next', self)
        next_button.clicked.connect(self.load_organization_units_step)
        program_indicator_layout.addWidget(next_button)

        program_indicator_page = QWidget(self)
        program_indicator_page.setLayout(program_indicator_layout)

        self.stacked_widget.addWidget(program_indicator_page)

    def select_all_program_indicators(self):
        """Select or deselect all program indicators based on the select all radio button"""
        select_all = self.select_all_radio_button.isChecked()
        for i in range(self.program_indicators_table.rowCount()):
            checkbox = self.program_indicators_table.cellWidget(i, 2)
            checkbox.setChecked(select_all)

    def load_organization_units_step(self):
        """Load organization units for selection"""
        url = self.url_input.text()
        username = self.username_input.text()
        password = self.password_input.text()

        try:
            response = requests.get(f"{url}/api/organisationUnitGroups", auth=(username, password))
            response.raise_for_status()
            org_unit_groups = response.json()['organisationUnitGroups']
            self.populate_organization_units(org_unit_groups)
            self.stacked_widget.setCurrentIndex(3)  # Move to period selection page
        except requests.exceptions.RequestException as e:
            self.show_error(f"Failed to load organization units: {e}")

    def populate_organization_units(self, org_unit_groups):
        """Populate organization unit selection dropdown"""
        self.org_unit_group_select = QComboBox(self)
        self.org_unit_group_select.clear()

        for group in org_unit_groups:
            group_name = group.get('displayName', 'Unnamed Group')
            self.org_unit_group_select.addItem(group_name, group['id'])

        org_unit_layout = QVBoxLayout()
        org_unit_layout.addWidget(QLabel("Select Organization Unit Group"))
        org_unit_layout.addWidget(self.org_unit_group_select)

        next_button = QPushButton('Next', self)
        next_button.clicked.connect(self.load_period_type_step)
        org_unit_layout.addWidget(next_button)

        org_unit_page = QWidget(self)
        org_unit_page.setLayout(org_unit_layout)

        self.stacked_widget.addWidget(org_unit_page)

    def load_period_type_step(self):
        """Load period types for selection"""
        url = self.url_input.text()
        username = self.username_input.text()
        password = self.password_input.text()

        try:
            response = requests.get(f"{url}/api/periodTypes", auth=(username, password))
            response.raise_for_status()
            period_types = response.json()['periodTypes']
            self.populate_period_types(period_types)
            self.stacked_widget.setCurrentIndex(4)  # Move to data preview page
        except requests.exceptions.RequestException as e:
            self.show_error(f"Failed to load period types: {e}")

    def populate_period_types(self, period_types):
        """Populate period types dropdown"""
        self.period_type_select = QComboBox(self)
        self.period_type_select.clear()

        for period_type in period_types:
            self.period_type_select.addItem(period_type.get('name', 'Unknown'), period_type.get('id'))

        period_layout = QVBoxLayout()
        period_layout.addWidget(QLabel("Select Period Type"))
        period_layout.addWidget(self.period_type_select)

        next_button = QPushButton('Next', self)
        next_button.clicked.connect(self.show_summary_page)
        period_layout.addWidget(next_button)

        period_page = QWidget(self)
        period_page.setLayout(period_layout)

        self.stacked_widget.addWidget(period_page)

    def show_summary_page(self):
        """Show a summary page of selected options"""
        summary_layout = QVBoxLayout()
        summary_layout.addWidget(QLabel(f"Selected Program Group: {self.selected_program_group}"))
        summary_layout.addWidget(QLabel(f"Selected Indicators: {len(self.selected_indicators)}"))
        summary_layout.addWidget(QLabel(f"Selected Organization Units: {self.org_unit_group_select.currentText()}"))
        summary_layout.addWidget(QLabel(f"Selected Period Type: {self.period_type_select.currentText()}"))

        export_button = QPushButton('Export Data', self)
        export_button.clicked.connect(self.export_data)
        summary_layout.addWidget(export_button)

        summary_page = QWidget(self)
        summary_page.setLayout(summary_layout)

        self.stacked_widget.addWidget(summary_page)

    def export_data(self):
        """Export data for selected program indicators"""
        # Logic for exporting data goes here
        print("Exporting data for selected program indicators...")

    def show_error(self, message):
        """Show error messages to the user"""
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setText(message)
        error_dialog.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DHIS2App()
    window.show()
    sys.exit(app.exec_())
