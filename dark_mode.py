def apply_dark_mode(app):
    dark_stylesheet = """
    QMainWindow {
        background-color: #2E2E2E;
        color: #FFFFFF;
    }
    
    QWidget {
        background-color: #2E2E2E;
        color: #FFFFFF;
    }
    
    QLineEdit {
        background-color: #4E4E4E;
        color: #FFFFFF;
        border: 1px solid #5A5A5A;
    }

    QPushButton {
        background-color: #4E4E4E;
        color: #FFFFFF;
        border: 1px solid #5A5A5A;
        padding: 5px;
    }
    
    QPushButton:hover {
        background-color: #5A5A5A;
    }
    
    QPushButton:pressed {
        background-color: #3E3E3E;
    }
    
    QLabel {
        color: #FFFFFF;
    }

    QListWidget {
        background-color: #2E2E2E;
        color: #FFFFFF;
        border: 1px solid #5A5A5A;
    }

    QProgressBar {
        background-color: #4E4E4E;
        color: #FFFFFF;
        border: 1px solid #5A5A5A;
    }
    
    QProgressBar::chunk {
        background-color: #0078d7;
    }

    QVBoxLayout, QHBoxLayout {
        background-color: #2E2E2E;
        color: #FFFFFF;
    }
    """
    app.setStyleSheet(dark_stylesheet)
