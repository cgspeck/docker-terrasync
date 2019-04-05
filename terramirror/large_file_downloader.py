import logging
from datetime import datetime
import os
from pathlib import Path
from urllib.parse import urlparse

import requests

from PyQt5.QtCore import QRunnable, pyqtSlot

from terramirror.config import Config
from terramirror.job_info import JobInfo
from terramirror.payload import DownloadLargeFilePayload
from terramirror.signals import WorkerSignals


class LargeFileDownloadWorker(QRunnable):

    def __init__(self, job_info: JobInfo, config: Config):
        super().__init__()
        self._job_info = job_info
        self._payload: DownloadLargeFilePayload = job_info.payload
        self._config: Config = config

        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        url = self._payload.url
        download_last_modified = self._payload.download_datetime.timestamp()
        destination = self._payload.destination
        expected_size = self._payload.download_size

        logging.info(f"Download start: {url} to {destination}")

        parent_path = Path(destination.parent)

        if not parent_path.exists():
            logging.info(f"Creating {parent_path}")
            parent_path.mkdir(parents=True, exist_ok=True)

        # download to foo.bar.tmp
        temp_path = Path(f"{destination}.tmp")
        logging.debug(f"Temporary download file is {temp_path}")

        if temp_path.exists():
            logging.debug(f"Removing existing temporary download file {temp_path}")
            os.remove(temp_path)

        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with temp_path.open('wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    logging.debug(f"Recieved {len(chunk)} bytes ({url})")
                    if chunk:
                        f.write(chunk)
                        f.flush()
                        os.fsync(f.fileno())
                f.flush()
                os.fsync(f.fileno())

        os.sync()
        logging.debug(f"Finished receiving data")
        # check download size against recieved data
        actual_download_size = os.stat(temp_path).st_size
        if actual_download_size != expected_size:
            raise RuntimeError(f"Downloading {url} failed because actual download size of {temp_path} ({actual_download_size}) does not match expected ({expected_size})")

        # after completion of download, delete existing file if any
        if destination.exists():
            logging.debug(f"Removing existing file at {destination}")
            os.remove(destination)
        # move into place after completion of download
        logging.debug(f"Renaming {temp_path} to {destination}")
        os.rename(temp_path, destination)
        os.sync()

        # set the file date/time
        os.utime(destination, times=(download_last_modified, download_last_modified))
        logging.info(f"Downloading complete: {destination}")
        self.signals.finished.emit(self._job_info)
