# downloader.py

import libtorrent as lt
import time
import threading
from PyQt5.QtCore import QObject, pyqtSignal

class TorrentDownloader(QObject):
    update_signal = pyqtSignal(object, object, bool, float, float, float, float)

    def __init__(self, torrent_url, save_path):
        super().__init__()
        self.torrent_url = torrent_url
        self.save_path = save_path
        self.session = lt.session()
        self.session.listen_on(6881, 6891)
        self.handle = None
        self.status = None
        self.add_torrent_from_url()
        self.download_thread = threading.Thread(target=self.download)
        self.download_thread.start()

    def add_torrent_from_url(self):
        params = {
            'save_path': self.save_path,
            'storage_mode': lt.storage_mode_t.storage_mode_sparse,
            'url': self.torrent_url
        }
        self.handle = self.session.add_torrent(params)
        self.status = self.handle.status()

    def download(self):
        while not self.handle.is_seed():
            self.status = self.handle.status()
            download_rate = self.status.download_rate / 1000  # kB/s
            total_downloaded = self.status.total_done / (1024 * 1024)  # MB
            total_size = self.status.total_wanted / (1024 * 1024)  # MB
            eta = (self.status.total_wanted - self.status.total_done) / self.status.download_rate if self.status.download_rate > 0 else 0  # seconds
            self.update_signal.emit(self.status, self, False, download_rate, total_downloaded, total_size, eta)
            time.sleep(1)
        self.update_signal.emit(self.status, self, True, 0, self.status.total_done / (1024 * 1024), self.status.total_wanted / (1024 * 1024), 0)

    def pause(self):
        if self.handle:
            self.handle.pause()

    def resume(self):
        if self.handle:
            self.handle.resume()

    def stop(self):
        if self.handle:
            self.session.remove_torrent(self.handle)
            self.handle = None
