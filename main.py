from gui import MainWindow
from PyQt5.QtWidgets import QApplication
from dark_mode import apply_dark_mode

if __name__ == "__main__":
    app = QApplication([])
    apply_dark_mode(app)
    window = MainWindow()
    window.show()
    app.exec_()
