import logging
from urllib.parse import urljoin

from bs4 import BeautifulSoup

import requests

from PyQt5.QtCore import QRunnable, pyqtSlot

from terramirror.config import Config
from terramirror.job_info import JobInfo
from terramirror.payload import AnalyseIndexPayload
from terramirror.signals import WorkerSignals


class DirectoryListWorker(QRunnable):

    def __init__(self, job_info: JobInfo, config: Config):
        super().__init__()
        self._job_info = job_info
        self._payload: AnalyseIndexPayload = job_info.payload
        self._config: Config = config

        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        url = self._payload.url
        logging.info(f"Analysing directory list at {url}")
        r = requests.get(url, headers=self._config.headers)
        r.raise_for_status()

        soup = BeautifulSoup(r.content, 'html.parser')

        links = soup.find_all('a')

        for link in links:
            href = link.get('href')

            if not href.startswith('http'):
                href = urljoin(url, href)

            if href.endswith('/'):
                self.signals.enqueue_directory_list_analysis.emit(href)
            else:
                self.signals.enqueue_download_analysis.emit(href)

        dir_index = urljoin(url, '.dirindex')

        r = requests.head(dir_index, headers=self._config.headers)

        if r.status_code == 200:
            self.signals.enqueue_download_analysis.emit(dir_index)

        logging.info(f"Finished analysing directory list at {url}")
        self.signals.finished.emit(self._job_info)
