import logging
from os import stat
from pathlib import Path
from urllib.parse import urlparse

import requests

from PyQt5.QtCore import QRunnable, pyqtSlot

from terramirror.config import Config
from terramirror.job_info import JobInfo
from terramirror.payload import AnalyseDownloadPayload
from terramirror.signals import WorkerSignals


class DownloadAnalyser(QRunnable):

    def __init__(self, job_info: JobInfo, config: Config):
        super().__init__()
        self._job_info = job_info
        self._payload: AnalyseDownloadPayload = job_info.payload
        self._config: Config = config

        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        url = self._payload.url
        logging.info(f"Analysing {url} for download")
        r = requests.head(url, headers=self._config.headers)
        r.raise_for_status()

        parsed_url = urlparse(url)
        parsed_url_path = parsed_url.path

        if parsed_url_path.startswith('/'):
            parsed_url_path = parsed_url_path[1:]

        download_size = int(r.headers['Content-Length'])
        file_name = parsed_url_path.split('/')[-1]
        file_path = '/'.join(parsed_url_path.split('/')[:-1])

        requires_download = False

        proposed_path = Path(self._config.destination, file_path, file_name)

        if not proposed_path.exists():
            requires_download = True
        else:
            if stat(proposed_path).st_size != download_size:
                requires_download = True

        if requires_download:
            logging.info(f"{url} requires downloading, queuing...")
            if download_size > self._config.large_download_threshold:
                self.signals.enqueue_large_download.emit(url, proposed_path)
            else:
                self.signals.enqueue_small_download.emit(url, proposed_path)

        self.signals.finished.emit(self._job_info)
