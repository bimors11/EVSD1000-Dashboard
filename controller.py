import sys
import serial
import time
import threading
import csv
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QFormLayout, QFrame, QLineEdit, QWidget, QPushButton, QComboBox, QVBoxLayout, QLabel, QTextEdit, QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView, QHBoxLayout
from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot
from PyQt5.QtGui import QTextCursor, QPixmap
import signal
import serial.tools.list_ports
import re

BAUD_RATE = 57600
MAIN_SCRIPT = 'execute.py'
CSV_FILENAME_TEMPLATE = '{}_stream_data.csv'
CSV_HEADER = {
    "VOR": [
        "RX", "STIOCPMV", "Index", "Date", "Time", "FREQ[MHz]", "MEAS.F[kHz]",
        "LEVEL[dBm]", "AM-MOD./30Hz[%]", "AM-MOD./9960Hz[%]", "FREQ_30[Hz]",
        "FREQ_9960[Hz]", "FREQ_FM30[Hz]", "BEARING(from)[°]", "FM-DEV.[Hz]",
        "FM-INDEX", "VOICE-MOD.[%]", "ID-MOD.[%]", "ID-F.[Hz]", "ID-CODE",
        "ID-Per.[s]", "Last_ID[s]", "DotLen[ms]", "DashLen[ms]", "DotDashGap[ms]",
        "Lettergap[ms]", "SubCarr_K2[dB]", "SubCarr_K3[dB]", "SubCarr_K4[dB]",
        "SubCarr_K5[dB]", "AM60Hz[%]", "AM1k44[%]", "AM1k50[%]", "No.Of Segm",
        "GPS_lat.", "GPS_long.", "GPS_alt[m]", "GPS_speed[km/h]", "GPS_date",
        "GPS_time", "GPS_Sat", "GPS_Status", "GPS_Fix", "GPS_HDOP", "GPS_VDOP",
        "GPS_Und.[m]", "Temp[°C]", "IFBW Manual", "MeasTime[ms]", "ATT.MODE",
        "BaseBand_Lev[V]", "BaseBand_DC[V]", "TrigCounter", "I/Q_Position",
        "I/Q_Samples", "x"
    ],
    "LLZ": [
        "RX", "STIOCPMV", "Index", "Date", "Time", "FREQ[MHz]", "SINGLE[kHz]", "CRS_UF[kHz]",
        "CLR_LF[kHz]", "LEVEL[dBm]", "AM-MOD./90Hz[%]", "AM-MOD./150Hz[%]", "FREQ_90[Hz]",
        "FREQ_150[Hz]", "DDM(90-150)[uA]", "SDM[%]", "PHI-90/150[°]", "ID-MOD.[%]", "ID-F.[Hz]",
        "ID-CODE", "ID-Per.[s]", "Last_ID[s]", "DotLen[ms]", "DashLen[ms]", "DotDashGap[ms]",
        "Lettergap[ms]", "LEV_CLR_LF[dBm]", "LEV_CRS_UF[dBm]", "AM-MOD_CLR_LF/90Hz[%]",
        "AM-MOD_CLR_LF/150Hz[%]", "FREQ_90_CLR_LF[Hz]", "FREQ_150_CLR_LF[Hz]", "DDM_CLR_LF(90-150)[1]",
        "SDM_CLR_LF[%]", "PHI-90/150_CLR_LF[°]", "AM-MOD_CRS_UF/90Hz[%]", "AM-MOD_CRS_UF/150Hz[%]",
        "FREQ_90_CRS_UF[Hz]", "FREQ_150_CRS_UF[Hz]", "DDM_CRS_UF(90-150)[1]", "SDM_CRS_UF[%]",
        "PHI-90/150_CRS_UF[°]", "PHI-90/90[°]", "PHI-150/150[°]", "ResFM90[Hz]", "ResFM150[Hz]",
        "K2/90Hz[%]", "K2/150Hz[%]", "K3/90Hz[%]", "K3/150Hz[%]", "K4/90Hz[%]", "K4/150Hz[%]",
        "THD/90Hz[%]", "THD/150Hz[%]", "AM240[%]", "GPS_lat.", "GPS_long.", "GPS_alt[m]",
        "GPS_speed[km/h]", "GPS_date", "GPS_time", "GPS_Sat", "GPS_Status", "GPS_Fix", "GPS_HDOP",
        "GPS_VDOP", "GPS_Und.[m]", "Temp[°C]", "MeasTime[ms]", "MeasMode", "LOC_GP", "ATT.MODE",
        "DemodOffset_1F[kHz]", "DemodOffset_CRS[kHz]", "DemodOffset_CLR[kHz]", "Autotune_1F",
        "Autotune_CRS", "Autotune_CLR", "IFBW_Man_WIDE", "IFBW_Man_UCLC", "BaseBand_Lev[V]",
        "BaseBand_DC[V]", "TrigCounter", "I/Q_Position", "I/Q_Samples", "x"
    ],
    "GP": [
        "RX", "STIOCPMV", "Index", "Date", "Time", "FREQ[MHz]", "SINGLE[kHz]", "CRS_UF[kHz]",
        "CLR_LF[kHz]", "LEVEL[dBm]", "AM-MOD./90Hz[%]", "AM-MOD./150Hz[%]", "FREQ_90[Hz]",
        "FREQ_150[Hz]", "DDM(90-150)[uA]", "SDM[%]", "PHI-90/150[°]", "ID-MOD.[%]", "ID-F.[Hz]",
        "ID-CODE", "ID-Per.[s]", "Last_ID[s]", "DotLen[ms]", "DashLen[ms]", "DotDashGap[ms]",
        "Lettergap[ms]", "LEV_CLR_LF[dBm]", "LEV_CRS_UF[dBm]", "AM-MOD_CLR_LF/90Hz[%]",
        "AM-MOD_CLR_LF/150Hz[%]", "FREQ_90_CLR_LF[Hz]", "FREQ_150_CLR_LF[Hz]", "DDM_CLR_LF(90-150)[1]",
        "SDM_CLR_LF[%]", "PHI-90/150_CLR_LF[°]", "AM-MOD_CRS_UF/90Hz[%]", "AM-MOD_CRS_UF/150Hz[%]",
        "FREQ_90_CRS_UF[Hz]", "FREQ_150_CRS_UF[Hz]", "DDM_CRS_UF(90-150)[1]", "SDM_CRS_UF[%]",
        "PHI-90/150_CRS_UF[°]", "PHI-90/90[°]", "PHI-150/150[°]", "ResFM90[Hz]", "ResFM150[Hz]",
        "K2/90Hz[%]", "K2/150Hz[%]", "K3/90Hz[%]", "K3/150Hz[%]", "K4/90Hz[%]", "K4/150Hz[%]",
        "THD/90Hz[%]", "THD/150Hz[%]", "AM240[%]", "GPS_lat.", "GPS_long.", "GPS_alt[m]",
        "GPS_speed[km/h]", "GPS_date", "GPS_time", "GPS_Sat", "GPS_Status", "GPS_Fix", "GPS_HDOP",
        "GPS_VDOP", "GPS_Und.[m]", "Temp[°C]", "MeasTime[ms]", "MeasMode", "LOC_GP", "ATT.MODE",
        "DemodOffset_1F[kHz]", "DemodOffset_CRS[kHz]", "DemodOffset_CLR[kHz]", "Autotune_1F",
        "Autotune_CRS", "Autotune_CLR", "IFBW_Man_WIDE", "IFBW_Man_UCLC", "BaseBand_Lev[V]",
        "BaseBand_DC[V]", "TrigCounter", "I/Q_Position", "I/Q_Samples", "x"
    ]
}

stop_event = threading.Event()
ser = None
recording = False
csv_writer = None
csv_file = None
current_mode = None

class Communicate(QObject):
    data_signal = pyqtSignal(str)

comm = Communicate()

def connect_to_raspi_via_serial(serial_port):
    global ser
    try:
        ser = serial.Serial(serial_port, BAUD_RATE, timeout=1)
        print("Connected to Raspberry Pi via serial port")
    except serial.SerialException as e:
        print(f"Serial connection error: {e}")

def login_to_raspberry_pi():
    global ser
    try:
        if ser is None or not ser.is_open:
            return False
        ser.write(b"beta\n")
        time.sleep(1)
        output = ser.read_until(b"Password: ").decode('utf-8')
        print(output.strip())
        ser.write(b"beta123\n")
        time.sleep(1)
        
        output = ser.read_until(b"$ ").decode('utf-8')
        print(output.strip())
        
        return True
    except Exception as e:
        print(f"Login error: {e}")
        return False

def start_recording():
    global recording, csv_writer, csv_file, current_mode
    if current_mode is None:
        print("Mode is not set. Cannot start recording.")
        return
    recording = True
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{current_mode}_{CSV_FILENAME_TEMPLATE.format(current_mode)}"
    csv_file = open(filename, 'w', newline='')
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(CSV_HEADER[current_mode])
    csv_file.flush()
    print(f"Recording started. Saving to {filename}")

def stop_recording():
    global recording, csv_writer, csv_file
    recording = False
    if csv_file:
        csv_file.close()
    csv_writer = None
    csv_file = None
    print("Recording stopped.")
    
def read_data_from_serial():
    global ser, csv_writer
    try:
        if ser is None or not ser.is_open:
            return
        while not stop_event.is_set():
            if ser.in_waiting > 0:
                data = ser.readline().decode('utf-8').strip()
                if recording and csv_writer:
                    data_list = data.split(',')
                    csv_writer.writerow(data_list)
                    csv_file.flush()
                print(data)
                comm.data_signal.emit(data)
    except serial.SerialException as e:
        print(f"Error: {e}")

def execute_script_on_raspberry_pi():
    global ser
    try:
        if ser is None or not ser.is_open:
            return
        ser.write(f"sudo python3 {MAIN_SCRIPT}\n".encode('utf-8'))
        time.sleep(1)
    except serial.SerialException as e:
        print(f"Error: {e}")

def signal_handler(sig, frame):
    stop_event.set()
    stop_recording()
    if ser and ser.is_open:
        ser.close()
    print("\nProgram terminated")
    sys.exit(0)

class App(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.current_mode = None
        self.current_frequency = None

    def initUI(self):
        self.setWindowTitle('EVSD1000 Controller')
        self.setStyleSheet("background-color: white;")

        main_layout = QVBoxLayout()

        # Create a horizontal layout for images
        image_layout = QHBoxLayout()

        # First image
        self.image_label1 = QLabel(self)
        pixmap1 = QPixmap('rsxbeta.png')  # Path to your first image file
        scaled_pixmap1 = pixmap1.scaled(300, 300, aspectRatioMode=1)  # Scale image to 100x100 while keeping aspect ratio
        self.image_label1.setPixmap(scaled_pixmap1)
        self.image_label1.setFixedSize(scaled_pixmap1.size())  # Set size to scaled image size
        image_layout.addWidget(self.image_label1)
        
        # Add the image layout to the main layout
        main_layout.addLayout(image_layout)

        # Add line above Streaming Status
        line = QFrame(self)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)

        # Connection status indicator
        connection_status_layout = QHBoxLayout()
        self.connection_status_label = QLabel('Connection Status', self)
        self.connection_status_label.setStyleSheet('font-size: 16px; color: black; font-weight: semibold;')
        connection_status_layout.addWidget(self.connection_status_label)
        self.connection_status_indicator = QLabel(self)
        self.connection_status_indicator.setStyleSheet('background-color: red; border-radius: 10px;')
        self.connection_status_indicator.setFixedSize(20, 20)
        connection_status_layout.addWidget(self.connection_status_indicator)

        main_layout.addLayout(connection_status_layout)

        # Layout for serial port combo and connect button
        top_layout = QHBoxLayout()

        self.serial_port_combo = QComboBox(self)
        self.serial_port_combo.setStyleSheet('color: black;')
        self.serial_port_combo.addItems(self.get_serial_ports())
        top_layout.addWidget(self.serial_port_combo)

        self.connect_btn = QPushButton('Connect to Telemetry', self)
        self.connect_btn.clicked.connect(self.connect_to_telem)
        self.connect_btn.setStyleSheet('color: black;')
        top_layout.addWidget(self.connect_btn)

        self.execute_btn = QPushButton('Connect to EVSD1000', self)
        self.execute_btn.clicked.connect(self.execute_script)
        self.execute_btn.setStyleSheet('color: black;')
        top_layout.addWidget(self.execute_btn)

        main_layout.addLayout(top_layout)

        # Add line above Streaming Status
        line = QFrame(self)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)


        # Streaming status indicator
        streaming_status_layout = QHBoxLayout()

        # Add label to display current mode

        self.streaming_status_label = QLabel('Streaming Status ', self)
        self.streaming_status_label.setStyleSheet('font-size: 16px; color: black; font-weight: semibold;')
        streaming_status_layout.addWidget(self.streaming_status_label)
        
        self.current_mode_label = QLabel('Current Mode: None', self)
        self.current_mode_label.setStyleSheet('font-size: 16px; color: black;')
        streaming_status_layout.addWidget(self.current_mode_label)

        self.streaming_status_indicator = QLabel(self)
        self.streaming_status_indicator.setStyleSheet('background-color: red; border-radius: 10px;')
        self.streaming_status_indicator.setFixedSize(20, 20)
        streaming_status_layout.addWidget(self.streaming_status_indicator)

        main_layout.addLayout(streaming_status_layout)

        # Mode selection
        mode_layout = QHBoxLayout()
        self.mode_dropdown = QComboBox(self)
        self.mode_dropdown.addItems(['VOR', 'LLZ', 'GP'])
        self.mode_dropdown.setStyleSheet('color: black;')
        mode_layout.addWidget(self.mode_dropdown)

        self.set_mode_btn = QPushButton('Set Mode', self)
        self.set_mode_btn.setStyleSheet('color: black;')
        self.set_mode_btn.clicked.connect(self.handle_mode_change)
        mode_layout.addWidget(self.set_mode_btn)

        main_layout.addLayout(mode_layout)

        # Frequency input
        freq_layout = QVBoxLayout()
        self.freq_input = QLineEdit(self)
        self.freq_input.setPlaceholderText('Enter frequency in MHz')
        self.freq_input.setStyleSheet('color: black;')
        freq_layout.addWidget(self.freq_input)

        self.set_freq_btn = QPushButton('Set Frequency', self)
        self.set_freq_btn.setStyleSheet('color: black;')
        self.set_freq_btn.clicked.connect(self.set_frequency)
        freq_layout.addWidget(self.set_freq_btn)

        main_layout.addLayout(freq_layout)

        # Streaming control
        control_layout = QHBoxLayout()
        self.start_streaming_btn = QPushButton('Start Streaming', self)
        self.start_streaming_btn.setStyleSheet('color: black;')
        self.start_streaming_btn.clicked.connect(self.start_streaming)
        control_layout.addWidget(self.start_streaming_btn)

        self.stop_btn = QPushButton('Stop Streaming', self)
        self.stop_btn.setStyleSheet('color: black;')
        self.stop_btn.clicked.connect(self.stop_streaming)
        control_layout.addWidget(self.stop_btn)

        #self.quit_btn = QPushButton('Close EVSD1000', self)
        #self.quit_btn.clicked.connect(self.send_ctrl_c)
        #control_layout.addWidget(self.quit_btn)
        
        main_layout.addLayout(control_layout)

        # Add line above Streaming Status
        line = QFrame(self)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)

        # Recording status indicator
        recording_status_layout = QHBoxLayout()
        self.recording_status_label = QLabel('Recording Status', self)
        self.recording_status_label.setStyleSheet('font-size: 16px; color: black;  font-weight: semibold;')
        recording_status_layout.addWidget(self.recording_status_label)
        self.recording_status_indicator = QLabel(self)
        self.recording_status_indicator.setStyleSheet('background-color: red; border-radius: 10px;')
        self.recording_status_indicator.setFixedSize(20, 20)
        recording_status_layout.addWidget(self.recording_status_indicator)

        main_layout.addLayout(recording_status_layout)

        # Recording controls
        recording_controls_layout = QHBoxLayout()
        self.start_recording_btn = QPushButton('Start Recording', self)
        self.start_recording_btn.setStyleSheet('color: black;')
        self.start_recording_btn.clicked.connect(self.start_recording)
        recording_controls_layout.addWidget(self.start_recording_btn)

        self.stop_recording_btn = QPushButton('Finish Recording', self)
        self.stop_recording_btn.setStyleSheet('color: black;')
        self.stop_recording_btn.clicked.connect(self.stop_recording)
        recording_controls_layout.addWidget(self.stop_recording_btn)

        main_layout.addLayout(recording_controls_layout)

        # Add line above Streaming Status
        line = QFrame(self)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)

        # Data display
        self.caption_label = QLabel("Terminal", self)
        self.caption_label.setStyleSheet('font-size: 16px; color: black;  font-weight: semibold;')
        main_layout.addWidget(self.caption_label)
        self.data_display = QTextEdit(self)
        self.data_display.setStyleSheet('color: black;')
        main_layout.addWidget(self.data_display)

        self.setLayout(main_layout)

        comm.data_signal.connect(self.update_data_display)

    def connect_to_telem(self):
        self.connect_to_raspi()
        self.login_to_raspi()
        if ser and ser.is_open:
            self.connection_status_indicator.setStyleSheet('background-color: green; border-radius: 10px;')
            self.data_display.append("Connected to Raspberry Pi via serial port.")
        else:
            self.connection_status_indicator.setStyleSheet('background-color: red; border-radius: 10px;')
            self.data_display.append("Failed to connect to Raspberry Pi.")

    def get_serial_ports(self):
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def connect_to_raspi(self):
        serial_port = self.serial_port_combo.currentText()
        connect_to_raspi_via_serial(serial_port)
        read_thread = threading.Thread(target=read_data_from_serial)
        read_thread.start()

    def login_to_raspi(self):
        if login_to_raspberry_pi():
            self.data_display.append("Login successful")
        else:
            self.data_display.append("Login failed")

    def execute_script(self):
        execute_script_on_raspberry_pi()

    def handle_mode_change(self):
        mode = self.mode_dropdown.currentText()  # Get the selected mode from the dropdown
        self.set_mode(mode)


    def set_mode(self, mode):
        if mode not in ['VOR', 'LLZ', 'GP']:
            self.data_display.append("Invalid mode selected. Please try again.")
            return

        self.current_mode = mode
        self.data_display.append(f"Mode set to: {mode}")
        self.current_mode_label.setText(f'Current Mode: {mode}')

        if mode == 'VOR':
            command = 'VOR\n'
        elif mode == 'LLZ':
            command = 'LLZ\n'
        elif mode == 'GP':
            command = 'GP\n'
        
        self.send_command(command)
        self.data_display.append("Mode selected. Please enter the frequency in MHz.")

    def set_frequency(self):
        frequency_str = self.freq_input.text().strip()
        try:
            frequency = float(frequency_str)
            if self.current_mode is None:
                self.data_display.append("Please select a mode before setting frequency.")
                return
            self.current_frequency = frequency

            freq_command = f"{frequency} MHz\n"
            self.send_command(freq_command)
            self.data_display.append(f"Frequency set to: {frequency} MHz")
        except ValueError:
            self.data_display.append("Invalid frequency input. Please enter a valid number.")

    def start_streaming(self):
        if self.current_frequency is None:
            self.data_display.append("Please set the frequency before starting streaming.")
            return
        self.send_command('STREAM\n')
        self.data_display.append("Started streaming.")

    def stop_streaming(self):
        self.send_command('STOP\n')
        self.streaming_status_indicator.setStyleSheet('background-color: red; border-radius: 10px;')
        self.data_display.append("Stopped streaming.")

    def start_recording(self):
        global recording, csv_writer, csv_file, current_mode
        if self.current_mode is None:
            self.data_display.append("Mode is not set. Cannot start recording.")
            return
        
        if self.current_mode not in CSV_HEADER:
            self.data_display.append(f"Invalid mode: {self.current_mode}")
            return

        recording = True
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        
        file_name = f"{timestamp}_{self.current_mode}_stream_data.csv"
        
        try:
            csv_file = open(file_name, 'w', newline='')
            csv_writer = csv.writer(csv_file)
            
            header = CSV_HEADER[self.current_mode]
            if header:
                csv_writer.writerow(header)
                self.data_display.append(f"Recording started in {self.current_mode} mode to {file_name}")
                self.recording_status_indicator.setStyleSheet('background-color: green; border-radius: 10px;')
            else:
                self.data_display.append(f"Header for mode {self.current_mode} is empty.")
                recording = False
                csv_file.close()
        except Exception as e:
            self.data_display.append(f"Error starting recording: {e}")
            recording = False

    def stop_recording(self):
        stop_recording()
        self.data_display.append("Stopped recording")
        self.recording_status_indicator.setStyleSheet('background-color: red; green; border-radius: 10px;')

    def send_command(self, command):
        global ser
        try:
            if ser and ser.is_open:
                ser.write(f"{command}".encode('utf-8'))
                self.data_display.append(f"Sent command: {command.strip()}")
                if command.startswith('STREAM'):
                    self.streaming_status_indicator.setStyleSheet('background-color: green; green; border-radius: 10px;')
                elif command == 'STOP':
                    self.streaming_status_indicator.setStyleSheet('background-color: red; green; border-radius: 10px;')
        except serial.SerialException as e:
            self.data_display.append(f"Error sending command: {e}")

    def send_ctrl_c(self):
        global ser
        try:
            if ser and ser.is_open:
                ser.write(b'\x03')
                self.data_display.append("Sent Ctrl+C")
        except serial.SerialException as e:
            self.data_display.append(f"Error sending Ctrl+C: {e}")

    @pyqtSlot(str)
    def update_data_display(self, data):
        ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
        cleaned_data = ansi_escape.sub('', data)
        self.data_display.append(cleaned_data)
        self.data_display.moveCursor(QTextCursor.End)

    def closeEvent(self, event):
        # Kirim Ctrl+C saat jendela ditutup
        self.send_ctrl_c()
        # Pastikan untuk menutup koneksi serial
        if ser and ser.is_open:
            ser.close()
        event.accept()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    
    read_thread = threading.Thread(target=read_data_from_serial)
    read_thread.start()
    
    try:
        sys.exit(app.exec_())
    finally:
        stop_event.set()
        read_thread.join()
        if ser and ser.is_open:
            ser.close()