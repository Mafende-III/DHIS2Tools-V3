import requests
import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QFileDialog, QMessageBox

class DHIS2DataSetRelatedDataelements(QWidget):
    def __init__(self):
        super().__init__()
        self.url_label = QLabel('URL:')
        self.url_input = QLineEdit()
        self.username_label = QLabel('Username:')
        self.username_input = QLineEdit()
        self.password_label = QLabel('Password:')
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.dataset_id_label = QLabel('Data Set ID:')
        self.dataset_id_input = QLineEdit()
        self.fetch_button = QPushButton('Fetch Data')
        self.save_button = QPushButton('Save Data to CSV')
        
        self.init_ui()
        self.data_elements_df = None
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(self.url_label)
        layout.addWidget(self.url_input)
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.dataset_id_label)
        layout.addWidget(self.dataset_id_input)
        layout.addWidget(self.fetch_button)
        layout.addWidget(self.save_button)
        
        self.setLayout(layout)
        self.setWindowTitle('DHIS2 Data Mapper')
        
        self.fetch_button.clicked.connect(self.fetch_data)
        self.save_button.clicked.connect(self.save_data_to_csv)
        
        self.save_button.setEnabled(False)
        
        self.show()
    
    def fetch_data(self):
        base_url = self.url_input.text()
        username = self.username_input.text()
        password = self.password_input.text()
        dataset_id = self.dataset_id_input.text()
        
        # Fetch the data elements and category option combinations
        self.data_elements_df = self.fetch_data_elements(base_url, username, password, dataset_id)
        
        if self.data_elements_df is not None:
            QMessageBox.information(self, 'Success', 'Data fetched successfully!')
            self.save_button.setEnabled(True)
        else:
            QMessageBox.critical(self, 'Error', 'Failed to fetch data.')

    def fetch_data_elements(self, base_url, username, password, dataset_id):
        auth = (username, password)
        dataset_url = f"{base_url}/api/dataSets/{dataset_id}.json?fields=dataSetElements[dataElement[id,name,categoryCombo[categoryOptionCombos[id,name]]]]"
        response = requests.get(dataset_url, auth=auth)
        
        if response.status_code != 200:
            return None
        
        dataset_data = response.json()
        
        data_elements_info = []
        for dataSetElement in dataset_data['dataSetElements']:
            data_element = dataSetElement['dataElement']
            data_element_id = data_element['id']
            data_element_name = data_element['name']
            
            for combo in data_element['categoryCombo']['categoryOptionCombos']:
                combo_id = combo['id']
                combo_name = combo['name']
                data_elements_info.append([data_element_id, data_element_name, combo_id, combo_name])
        
        df = pd.DataFrame(data_elements_info, columns=['Data Element ID', 'Data Element Name', 'Category Option Combo ID', 'Category Option Combo Name'])
        return df
    
    def save_data_to_csv(self):
        if self.data_elements_df is not None:
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Data to CSV", "", "CSV Files (*.csv);;All Files (*)", options=options)
            if file_path:
                self.data_elements_df.to_csv(file_path, index=False)
                QMessageBox.information(self, 'Success', 'Data saved successfully!')
        else:
            QMessageBox.critical(self, 'Error', 'No data to save.')

if __name__ == '__main__':
    app = QApplication([])
    window = DHIS2DataSetRelatedDataelements()
    app.exec_()
