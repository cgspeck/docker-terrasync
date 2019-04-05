import logging
from datetime import datetime
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

        parsed_url = urlparse(url)
        parsed_url_path = parsed_url.path

        if parsed_url_path.startswith('/'):
            parsed_url_path = parsed_url_path[1:]

        file_name = parsed_url_path.split('/')[-1]
        file_path = '/'.join(parsed_url_path.split('/')[:-1])

        mirror_url = urlparse(self._config.mirror)
        mirror_path = mirror_url.path

        requires_download = False

        if mirror_path.startswith('/'):
            mirror_path = mirror_path[1:]

        file_path_frags = file_path.split(mirror_path)

        if len(file_path_frags) == 1:
            file_path = ''
        else:
            file_path = file_path_frags[1]

        proposed_path = Path(self._config.destination, file_path, file_name)

        r = requests.head(url, headers=self._config.headers)
        r.raise_for_status()
        download_size = int(r.headers['Content-Length'])


        if not proposed_path.exists():
            requires_download = True
        else:
            if stat(proposed_path).st_size != download_size:
                requires_download = True
            # TODO: add a last-modified date check

        if requires_download:
            logging.info(f"{url} requires downloading to {proposed_path}, queuing...")
            # : 'Mon, 01 Apr 2019 10:35:57 GMT'
            last_modified_str = r.headers['Last-Modified']
            last_modified_datetime = datetime.strptime(last_modified_str, '%a, %d %b %Y %H:%M:%S %Z')

            if download_size > self._config.large_download_threshold:
                self.signals.enqueue_large_download.emit(url, proposed_path, download_size, last_modified_datetime)
            else:
                self.signals.enqueue_small_download.emit(url, proposed_path, download_size, last_modified_datetime)

        self.signals.finished.emit(self._job_info)
