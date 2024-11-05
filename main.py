import sys
from PyQt5.QtWidgets import QApplication
from ui import DataPlotter

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DataPlotter()
    window.showMaximized()
    sys.exit(app.exec_())
