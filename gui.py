# gui.py

import sys
import qtawesome as qta
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                             QPushButton, QLabel, QFileDialog, QProgressBar, 
                             QHBoxLayout, QListWidget, QListWidgetItem, QLineEdit, 
                             QMessageBox, QSizePolicy, QSystemTrayIcon, QMenu, QAction, 
                             QDockWidget, QMenuBar, QStatusBar, QToolBar)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QIcon
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

        self.dark_mode = False

        # Tray icon setup
        self.tray_icon = QSystemTrayIcon(self.get_icon('fa5s.cloud-download-alt'), self)
        self.tray_icon.setToolTip("Torrent Downloader")
        tray_menu = QMenu()
        restore_action = QAction("Restore", self)
        quit_action = QAction("Quit", self)
        tray_menu.addAction(restore_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)

        restore_action.triggered.connect(self.show)
        quit_action.triggered.connect(QApplication.instance().quit)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

        # Show tray icon
        self.tray_icon.show()

        # Navbar setup
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        view_menu = menubar.addMenu("View")
        help_menu = menubar.addMenu("Help")

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu actions
        toggle_sidebar_action = QAction("Toggle Sidebar", self)
        toggle_sidebar_action.triggered.connect(self.toggle_sidebar)
        view_menu.addAction(toggle_sidebar_action)

        toggle_dark_mode_action = QAction("Toggle Dark Mode", self)
        toggle_dark_mode_action.triggered.connect(self.toggle_dark_mode)
        view_menu.addAction(toggle_dark_mode_action)

        # Status bar setup
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Toolbar setup for the first sidebar
        self.toolbar = QToolBar("Main Toolbar")
        self.addToolBar(Qt.LeftToolBarArea, self.toolbar)
        
        self.download_action = QAction(self.get_icon('fa5s.download'), "Mengunduh", self)
        self.waiting_action = QAction(self.get_icon('fa5s.pause'), "Menunggu", self)
        self.stopped_action = QAction(self.get_icon('fa5s.stop'), "Terhenti", self)

        self.toolbar.addAction(self.download_action)
        self.toolbar.addAction(self.waiting_action)
        self.toolbar.addAction(self.stopped_action)

        self.download_action.triggered.connect(lambda: self.switch_sidebar("Mengunduh"))
        self.waiting_action.triggered.connect(lambda: self.switch_sidebar("Menunggu"))
        self.stopped_action.triggered.connect(lambda: self.switch_sidebar("Terhenti"))

        # Sidebar setup for the second sidebar
        self.sidebar = QDockWidget("Sidebar", self)
        self.sidebar.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        sidebar_content = QWidget()
        self.sidebar_layout = QVBoxLayout()
        self.sidebar_list = QListWidget()
        self.sidebar_list.addItem("Mengunduh")
        self.sidebar_list.addItem("Menunggu")
        self.sidebar_list.addItem("Terhenti")
        self.sidebar_list.currentItemChanged.connect(self.on_sidebar_item_changed)
        self.sidebar_layout.addWidget(self.sidebar_list)
        sidebar_content.setLayout(self.sidebar_layout)
        self.sidebar.setWidget(sidebar_content)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.sidebar)

        # Ensure the sidebar can be dragged and docked freely
        self.sidebar.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)

        # Content area setup
        self.content_area = QWidget()
        self.setCentralWidget(self.content_area)
        self.content_layout = QVBoxLayout()

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
        self.content_layout.addWidget(self.url_input)
        self.content_layout.addLayout(self.control_layout)
        self.content_layout.addWidget(self.download_list)
        self.content_area.setLayout(self.content_layout)

        self.downloaders = {'Mengunduh': [], 'Menunggu': [], 'Terhenti': []}

        self.setWindowIcon(self.get_icon('fa5s.cloud-download-alt'))
        self.setWindowTitle("Torrent Downloader")

        self.update_styles()  # Apply initial styles

    def get_icon(self, name):
        if self.dark_mode:
            return qta.icon(name, color='white')
        else:
            return qta.icon(name, color='black')

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self.update_icons()
        self.update_styles()

    def update_icons(self):
        self.tray_icon.setIcon(self.get_icon('fa5s.cloud-download-alt'))
        self.setWindowIcon(self.get_icon('fa5s.cloud-download-alt'))
        self.download_action.setIcon(self.get_icon('fa5s.download'))
        self.waiting_action.setIcon(self.get_icon('fa5s.pause'))
        self.stopped_action.setIcon(self.get_icon('fa5s.stop'))

    def update_styles(self):
        if self.dark_mode:
            self.setStyleSheet("""
                QMainWindow {background-color: #2e2e2e; color: white;}
                QPushButton {
                    background-color: #444444;
                    color: white;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #555555;
                    border: 1px solid #666666;
                }
                QLineEdit {
                    background-color: #444444;
                    color: white;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    padding: 5px;
                }
                QListWidget {
                    background-color: #3e3e3e;
                    color: white;
                    border: 1px solid #555555;
                }
                QProgressBar {
                    background-color: #3e3e3e;
                    color: white;
                    border: 1px solid #555555;
                    text-align: center;
                }
                QLabel {
                    color: white;
                }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow {background-color: white; color: black;}
                QPushButton {
                    background-color: #f0f0f0;
                    color: black;
                    border: 1px solid #d0d0d0;
                    border-radius: 4px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                    border: 1px solid #c0c0c0;
                }
                QLineEdit {
                    background-color: white;
                    color: black;
                    border: 1px solid #d0d0d0;
                    border-radius: 4px;
                    padding: 5px;
                }
                QListWidget {
                    background-color: white;
                    color: black;
                    border: 1px solid #d0d0d0;
                }
                QProgressBar {
                    background-color: white;
                    color: black;
                    border: 1px solid #d0d0d0;
                    text-align: center;
                }
                QLabel {
                    color: black;
                }
            """)

    def toggle_sidebar(self):
        if self.sidebar.isVisible():
            self.sidebar.hide()
        else:
            self.sidebar.show()

    def switch_sidebar(self, category):
        self.sidebar_list.clear()
        self.sidebar_list.addItem(category)

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

        pause_button = QPushButton(self.get_icon('fa5s.pause'), "")
        pause_button.setFixedHeight(40)
        pause_button.setFont(QFont("Arial", 14))
        pause_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        pause_button.clicked.connect(lambda: self.pause_download(downloader, item))
        
        resume_button = QPushButton(self.get_icon('fa5s.play'), "")
        resume_button.setFixedHeight(40)
        resume_button.setFont(QFont("Arial", 14))
        resume_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        resume_button.clicked.connect(lambda: self.resume_download(downloader, item))
        
        stop_button = QPushButton(self.get_icon('fa5s.stop'), "")
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
        for downloader in self.downloaders.get(category, []):
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

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Torrent Downloader",
            "The application is still running in the system tray.",
            QSystemTrayIcon.Information,
            2000
        )

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.show()


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
