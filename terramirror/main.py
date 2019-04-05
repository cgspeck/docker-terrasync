from datetime import datetime
from pathlib import Path
import logging
import sys

from urllib.parse import urlparse

from PyQt5.QtCore import QCoreApplication, QThreadPool, pyqtSlot

from terramirror.directory_list_analyser import DirectoryListWorker
from terramirror.download_analyser import DownloadAnalyser
from terramirror.job_info import JobInfo
from terramirror.instructions import Instruction
from terramirror.large_file_downloader import LargeFileDownloadWorker
from terramirror.payload import AnalyseIndexPayload, AnalyseDownloadPayload, DownloadLargeFilePayload


class Main(QCoreApplication):
    def __init__(self, config):
        super(Main, self).__init__(sys.argv)
        self._config = config
        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

        self._mirror_url = config.mirror
        self._total_jobs = 1
        self._job_count = 1

        self._enqueue_directory_list_analysis(self._mirror_url)
        self._urls_analyised = set()
        self._urls_downloaded = set()

        if config.test_mode:
            self._test_dir_analysis = 0
            self._test_large_downloads = 0
            self._test_analyise_download = 0

    def _enqueue_directory_list_analysis(self, url):
        job_info = JobInfo(
            Instruction.ANALYSE_DIRECTORY_LIST,
            AnalyseIndexPayload(url)
        )
        worker = self._create_directory_list_analysis_worker(job_info)
        # Execute
        self.threadpool.start(worker)

    def _create_directory_list_analysis_worker(self, job_info):
        worker = DirectoryListWorker(job_info, self._config)
        worker.signals.finished.connect(self.handle_finished_job)
        worker.signals.enqueue_directory_list_analysis.connect(self.enqueue_directory_list_analysis)
        worker.signals.enqueue_download_analysis.connect(self.enqueue_download_analysis)
        worker.signals.enqueue_small_download.connect(self.enqueue_large_download)
        return worker

    @pyqtSlot(str)
    def enqueue_download_analysis(self, url: str):
        logging.debug(f"enqueue_download_analysis recieved with {url}")
        if self._validate_url(url):
            logging.debug(f"URL {url} passed validation")

            if self._config.test_mode:
                self._test_analyise_download += 1
                if self._test_analyise_download > 30:
                    logging.debug("Not doing enqueue_download_analysis, in test mode")
                    return

            self._job_count += 1
            self._total_jobs += 1
            job_info = JobInfo(
                Instruction.ANALYSE_DOWNLOAD_CANDIDATE,
                AnalyseDownloadPayload(url)
            )
            worker = self._create_download_analysis_worker(job_info)
            # Execute
            self.threadpool.start(worker)

    def _create_download_analysis_worker(self, job_info):
        worker = DownloadAnalyser(job_info, self._config)
        worker.signals.finished.connect(self.handle_finished_job)
        worker.signals.enqueue_small_download.connect(self.enqueue_large_download)
        worker.signals.enqueue_large_download.connect(self.enqueue_large_download)
        return worker

    @pyqtSlot(str, Path, int, datetime)
    def enqueue_large_download(self, url: str, proposed_path: Path, download_size: int, download_datetime: datetime):
        logging.debug(f"enqueue_large_download recieved with {url}")

        if url in self._urls_downloaded:
            logging.debug(f"{url} has already been downloaded!")
            return

        if self._config.test_mode:
            self._test_large_downloads += 1
            if self._test_large_downloads > 30:
                logging.debug("Not doing enqueue_large_download, in test mode")
                return

        self._job_count += 1
        self._total_jobs += 1
        job_info = JobInfo(
            Instruction.DOWNLOAD_SMALL_FILE,
            DownloadLargeFilePayload(
                url,
                destination=proposed_path,
                download_size=download_size,
                download_datetime=download_datetime
            )
        )
        worker = self._create_large_downloader_worker(job_info)
        self.threadpool.start(worker)

    def _create_large_downloader_worker(self, job_info):
        worker = LargeFileDownloadWorker(job_info, self._config)
        worker.signals.finished.connect(self.handle_finished_job)
        return worker

    @pyqtSlot(str)
    def enqueue_directory_list_analysis(self, url: str):
        logging.info(f"enqueue_directory_list_analysis recieved with {url}")

        if self._validate_url(url):
            logging.info(f"URL {url} passed validation, queuing")

            if self._config.test_mode:
                self._test_dir_analysis += 1
                if self._test_dir_analysis > 30:
                    logging.info("Not queuing directory analysis, in test mode")
                    return

            self._job_count += 1
            self._total_jobs += 1
            self._enqueue_directory_list_analysis(url)

    def _validate_url(self, url):
        logging.debug(f"Validaing url {url}")
        if url in self._urls_analyised:
            logging.debug(f"Not queuing already seen url {url}")
            return False

        self._urls_analyised.add(url)

        candidate = urlparse(url)
        mirror = urlparse(self._mirror_url)

        if mirror.netloc != candidate.netloc:
            logging.debug(f"Url {url} is not on same host as mirror!")
            return False

        if len(candidate.params) != 0:
            logging.debug(f"Url {url} has params!")
            return False

        if len(candidate.query) != 0:
            logging.debug(f"Url {url} has a query string!")
            return False

        if len(candidate.fragment) != 0:
            logging.debug(f"Url {url} has fragments!")
            return False

        return True

    @pyqtSlot(JobInfo)
    def handle_finished_job(self, job_info: JobInfo):
        self._job_count -= 1
        logging.debug(f"Handle_Finished recieved job info: {job_info}")
        logging.debug(f"Job count: {self._job_count} Active thread count: {self.threadpool.activeThreadCount()}")

        if self._job_count == 0:
            logging.info("All done!")
            self.exit(0)

        if self._total_jobs >= 10000:
            logging.debug("Exit for test!")
            self.threadpool.clear()
            self.exit(0)

    @pyqtSlot(JobInfo, Exception)
    def handle_failed_job(self, job_info: JobInfo, execption: Exception = None):
        msg = f"handle_failed_job recieved {job_info}"
        if execption is not None:
            msg += f" with exception: {execption}"

        logging.error(msg)

        self._job_count -= 1

        if job_info.attempt_number >= 3:
            raise RuntimeError(f"Job failed three times: {job_info}")

        job_info.attempt_number += 1

        if job_info.instruction == Instruction.ANALYSE_DIRECTORY_LIST:
            worker = self._create_directory_list_analysis_worker(job_info)
        elif job_info.instruction == Instruction.ANALYSE_DOWNLOAD_CANDIDATE:
            worker = self._create_download_analysis_worker(job_info)
        elif job_info.instruction in [Instruction.DOWNLOAD_SMALL_FILE, Instruction.DOWNLOAD_LARGE_FILE]:
            worker = self._create_large_downloader_worker(job_info)

        logging.info("Requeuing job")
        self.threadpool.start(worker)


if __name__ == "__main__":
    import sys
    main = Main(sys.argv)
    sys.exit(main.exec_())

