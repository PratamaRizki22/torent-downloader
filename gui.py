# gui.py

from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                             QPushButton, QLabel, QFileDialog, QProgressBar, 
                             QHBoxLayout, QListWidget, QListWidgetItem, QLineEdit, QMessageBox, QSizePolicy)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont
from downloader import TorrentDownloader

def format_eta(seconds):
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Torrent Downloader')
        self.setGeometry(100, 100, 1200, 800)

        # Main layout
        self.main_layout = QVBoxLayout()

        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.addItem("Mengunduh")
        self.sidebar.addItem("Menunggu")
        self.sidebar.addItem("Terhenti")
        self.sidebar.currentItemChanged.connect(self.on_sidebar_item_changed)
        
        # Content area
        self.content_area = QVBoxLayout()

        # URL input
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter torrent URL here")
        self.url_input.setFixedHeight(40)
        self.url_input.setFont(QFont("Arial", 12))
        
        # Download list
        self.download_list = QListWidget()

        # Control buttons
        self.control_layout = QHBoxLayout()
        self.start_button = QPushButton('Start Download')
        self.start_button.setFixedHeight(40)
        self.start_button.setFont(QFont("Arial", 12))
        self.start_button.clicked.connect(self.start_download)
        self.control_layout.addWidget(self.start_button)
        
        # Adding widgets to the main layout
        main_container = QHBoxLayout()
        main_container.addWidget(self.sidebar)
        main_container.addLayout(self.content_area)

        self.content_area.addWidget(self.url_input)
        self.content_area.addLayout(self.control_layout)
        self.content_area.addWidget(self.download_list)

        # Set central widget
        container = QWidget()
        container.setLayout(main_container)
        self.setCentralWidget(container)

        self.downloaders = {'Mengunduh': [], 'Menunggu': [], 'Terhenti': []}

    def start_download(self):
        torrent_url = self.url_input.text().strip()
        save_path = QFileDialog.getExistingDirectory(self, "Select Save Directory")
        if save_path and torrent_url:
            downloader = TorrentDownloader(torrent_url=torrent_url, save_path=save_path)
            downloader.update_signal.connect(self.update_status)
            self.downloaders['Mengunduh'].append(downloader)
            self.add_download_item(torrent_url, downloader, 'Mengunduh')

    def add_download_item(self, torrent_name, downloader, category):
        item = QListWidgetItem(torrent_name)
        item.setFont(QFont("Arial", 14))
        progress_bar = QProgressBar()
        progress_bar.setAlignment(Qt.AlignCenter)
        progress_bar.setValue(0)
        progress_bar.setFixedHeight(40)
        progress_bar.setFont(QFont("Arial", 14))
        item.setSizeHint(progress_bar.sizeHint())

        pause_button = QPushButton("Pause")
        pause_button.setFixedHeight(40)
        pause_button.setFont(QFont("Arial", 14))
        pause_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        pause_button.clicked.connect(lambda: self.pause_download(downloader, item))
        
        resume_button = QPushButton("Resume")
        resume_button.setFixedHeight(40)
        resume_button.setFont(QFont("Arial", 14))
        resume_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        resume_button.clicked.connect(lambda: self.resume_download(downloader, item))
        
        stop_button = QPushButton("Stop")
        stop_button.setFixedHeight(40)
        stop_button.setFont(QFont("Arial", 14))
        stop_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        stop_button.clicked.connect(lambda: self.stop_download(downloader, item))
        
        details_label = QLabel("")
        details_label.setFixedHeight(40)
        details_label.setFont(QFont("Arial", 14))
        
        hbox = QHBoxLayout()
        hbox.addWidget(progress_bar)
        hbox.addWidget(pause_button)
        hbox.addWidget(resume_button)
        hbox.addWidget(stop_button)
        
        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(details_label)
        
        widget = QWidget()
        widget.setLayout(vbox)
        
        self.download_list.addItem(item)
        self.download_list.setItemWidget(item, widget)

    def pause_download(self, downloader, item):
        downloader.pause()
        self.move_item_to_category(item, downloader, 'Menunggu')

    def resume_download(self, downloader, item):
        downloader.resume()
        self.move_item_to_category(item, downloader, 'Mengunduh')

    def stop_download(self, downloader, item):
        downloader.stop()
        item.setHidden(True)
        QMessageBox.information(self, "Download Stopped", "The download has been stopped.")
        self.move_item_to_category(item, downloader, 'Terhenti')

    def move_item_to_category(self, item, downloader, category):
        for cat in self.downloaders:
            if downloader in self.downloaders[cat]:
                self.downloaders[cat].remove(downloader)
        self.downloaders[category].append(downloader)
        self.update_list_display(category)

    def update_list_display(self, category):
        self.download_list.clear()
        for downloader in self.downloaders[category]:
            self.add_download_item(downloader.torrent_url, downloader, category)

    def update_status(self, status, downloader, finished, download_rate, total_downloaded, total_size, eta):
        for i in range(self.download_list.count()):
            item = self.download_list.item(i)
            widget = self.download_list.itemWidget(item)
            progress_bar = widget.layout().itemAt(0).layout().itemAt(0).widget()
            details_label = widget.layout().itemAt(1).widget()
            if isinstance(progress_bar, QProgressBar):
                if status and downloader:
                    progress_value = int(status.progress * 100)
                    progress_bar.setValue(progress_value)
                    progress_bar.setFormat(f"{progress_value}%")

                    eta_str = format_eta(eta) if eta > 0 else "N/A"
                    details_text = (f"{total_downloaded:.2f} MB / {total_size:.2f} MB "
                                    f"@ {download_rate:.2f} kB/s - {eta_str}")
                    details_label.setText(details_text)
                if finished:
                    progress_bar.setFormat("Download Complete")
                    details_label.setText(f"{total_downloaded:.2f} MB / {total_size:.2f} MB - Download Complete")
                    self.move_item_to_category(item, downloader, 'Terhenti')

    def on_sidebar_item_changed(self, current, previous):
        if current:
            category = current.text()
            self.update_list_display(category)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
