import os
from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QPushButton, QVBoxLayout, QSizePolicy, QSpacerItem, QHBoxLayout, QLabel

def is_csv_file(file_path):
    return file_path.endswith('.csv')

def get_latest_csv_files():
    try:
        csv_files = [f for f in os.listdir('.') if is_csv_file(f)]

        latest_files = {'VOR': None, 'LLZ': None, 'GP': None}

        for csv_file in csv_files:
            if 'VOR' in csv_file:
                if latest_files['VOR'] is None or os.path.getmtime(csv_file) > os.path.getmtime(latest_files['VOR']):
                    latest_files['VOR'] = csv_file
            elif 'LLZ' in csv_file:
                if latest_files['LLZ'] is None or os.path.getmtime(csv_file) > os.path.getmtime(latest_files['LLZ']):
                    latest_files['LLZ'] = csv_file
            elif 'GP' in csv_file:
                if latest_files['GP'] is None or os.path.getmtime(csv_file) > os.path.getmtime(latest_files['GP']):
                    latest_files['GP'] = csv_file

        latest_files = {k: v for k, v in latest_files.items() if v is not None}
        print(f"Filtered latest files: {latest_files}")

        return latest_files.values()
    except Exception as e:
        print(f"Error in get_latest_csv_files: {e}")
        return []
    
def detect_mode(self):
    if 'VOR' in self.file_path:
        self.mode = 'VOR'
    elif 'LLZ' in self.file_path:
        self.mode = 'LLZ'
    elif 'GP' in self.file_path:
        self.mode = 'GP'
    else:
        self.mode = ''
    self.update_checkboxes_based_on_mode()
    self.prompt_for_bounds()


def get_bounds_inputs(mode, columns):
    dialog = QDialog()
    dialog.setWindowTitle(f'Enter Bounds for {mode}')
    dialog.setStyleSheet("background-color: white; color: black;")
    dialog.setFixedSize(550, 450)

    main_layout = QVBoxLayout()
    form_layout = QFormLayout()
    form_layout.setSpacing(20)

    bound_inputs = {}

    for column in columns:
        upper_bound_input = QLineEdit()
        lower_bound_input = QLineEdit()
        form_layout.addRow(QLabel(f'Upper Bound for {column}:'), upper_bound_input)
        form_layout.addRow(QLabel(f'Lower Bound for {column}:'), lower_bound_input)
        bound_inputs[column] = (upper_bound_input, lower_bound_input)

    main_layout.addLayout(form_layout)

    button_layout = QHBoxLayout()
    ok_button = QPushButton('OK')

    button_layout.addWidget(ok_button)
    main_layout.addLayout(button_layout)
    dialog.setLayout(main_layout)

    def on_ok_clicked():
        try:
            bounds = {}
            for column, inputs in bound_inputs.items():
                upper_bound = float(inputs[0].text())
                lower_bound = float(inputs[1].text())
                bounds[column] = (upper_bound, lower_bound)
            dialog.accept()
            return bounds
        except ValueError:
            # Handle invalid input
            pass

    ok_button.clicked.connect(on_ok_clicked)

    result = dialog.exec()

    if result == QDialog.Accepted:
        try:
            return {column: (float(inputs[0].text()), float(inputs[1].text())) for column, inputs in bound_inputs.items()}
        except ValueError:
            return None
    else:
        return None

def get_user_inputs():
    dialog = QDialog()
    dialog.setWindowTitle('Enter DetaLLZ')
    dialog.setStyleSheet("background-color: white; color: black;")
    
    dialog.setFixedSize(400, 200)

    main_layout = QVBoxLayout()

    form_layout = QFormLayout()
    form_layout.setSpacing(20)

    bandara = QLineEdit()
    alat = QLineEdit()
    pengujian = QLineEdit()

    form_layout.addRow('Airport:', bandara)
    form_layout.addRow('Transmitter:', alat)
    form_layout.addRow('Attempts:', pengujian)

    main_layout.addLayout(form_layout)

    main_layout.addStretch()

    buttons_layout = QHBoxLayout()
    ok_button = QPushButton('OK')

    buttons_layout.addWidget(ok_button)

    main_layout.addLayout(buttons_layout)

    dialog.setLayout(main_layout)

    def validate_fields():
        ok_button.setEnabled(bandara.text().strip() != '' and 
                             alat.text().strip() != '' and 
                             pengujian.text().strip() != '')
    
    def on_text_changed():
        validate_fields()
    
    bandara.textChanged.connect(on_text_changed)
    alat.textChanged.connect(on_text_changed)
    pengujian.textChanged.connect(on_text_changed)

    def on_ok_clicked():
        if bandara.text().strip() and alat.text().strip() and pengujian.text().strip():
            dialog.accept()
    
    ok_button.clicked.connect(on_ok_clicked)

    validate_fields()
    
    result = dialog.exec()
    
    if result == QDialog.Accepted:
        return bandara.text(), alat.text(), pengujian.text()
    else:
        return None