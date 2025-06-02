import sys
import os
from Search import search
from Parser import parse
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QDialog, QLineEdit, QPushButton, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QComboBox, QMessageBox, QHBoxLayout

# Set the working directory to the script directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

class Form(QDialog):

    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.setWindowTitle("Search Form")
        total_w = 500
        self.resize(total_w, 600)

        # Initialize the UI components
        self.G_text = QLabel("General Search:")
        self.N_text = QLabel("How many results?")
        self.sort_label = QLabel("Sorting:")
        self.sort_order = "Descending"

        self.General_Search = QLineEdit("")
        self.General_Search.setFixedWidth(250)  # Set the width of the search input
        self.Number_Results = QLineEdit("")
        self.Number_Results.setFixedWidth(250)  

        self.button = QPushButton("Search")
        self.button.setFixedWidth(100)  
        self.table = QTableWidget()

        self.combo_box = QComboBox()
        self.combo_box.setFixedWidth(87) 


        # Add items to the dropdown for sorting
        self.combo_box.addItem("Descending")
        self.combo_box.addItem("Ascending")

        # Set up the table
        self.table.setRowCount(20)
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Título", "Data"])
        self.table.setColumnWidth(1, 100)  # Set the width of the second column (index 1) to 150 pixels
        self.table.setColumnWidth(0, total_w-150)  # Set the width of the first column (index 0) to 200 pixels


        h_layout1 = QHBoxLayout()
        h_layout2 = QHBoxLayout()

        # Create layout and add widgets
        layout = QVBoxLayout(self)
        h_layout1.addWidget(self.G_text)
        h_layout2.addWidget(self.General_Search)
        h_layout1.addWidget(self.N_text)
        h_layout2.addWidget(self.Number_Results)
        layout.addLayout(h_layout1)  # Add first horizontal layout to the main vertical layout
        layout.addLayout(h_layout2)  # Add second horizontal layout to the main vertical layout
        layout.addWidget(self.sort_label)
        layout.addWidget(self.combo_box)
        layout.addWidget(self.button)
        layout.addWidget(self.table)

        # Connect button and combo box actions
        self.button.clicked.connect(self.search_function)
        self.combo_box.currentTextChanged.connect(self.on_combobox_changed)

    def on_combobox_changed(self, text):
        self.sort_order = text

    def search_function(self):
        # Retrieve input values
        query = self.General_Search.text()
        
        try:
            if not self.Number_Results.text():
                N_R = 2000
            else:
                N_R = int(self.Number_Results.text())
        except ValueError:
            self.show_error("Please enter a valid number for results.")
            return

        # Validate the number of results
        if N_R <= 0 or N_R > 10000:
            self.show_error(f"Number of results must be between 1 and 10,000 not {N_R}")
            return

        if not query.strip():
            self.show_error("Please enter a search query.")
            return

        # Execute search
        results = parse(search(query, N_R, self.sort_order), self.sort_order)

        if not results:
            self.show_error("No results found or an issue with the scraper.")
            return

        # Populate the table with the results
        self.table.setRowCount(len(results))
        for idx, result in enumerate(results):
            title_item = QTableWidgetItem(result[0])
            date_item = QTableWidgetItem(result[1])
            self.table.setItem(idx, 0, title_item)
            self.table.setItem(idx, 1, date_item)

        # print(f"Search: {query}. {N_R} Results.")

    def show_error(self, message):
        """Displays an error message in a message box."""
        error_dialog = QMessageBox(self)
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setWindowTitle("Error")
        error_dialog.setText(message)
        error_dialog.exec()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = Form()
    form.show()
    sys.exit(app.exec())
