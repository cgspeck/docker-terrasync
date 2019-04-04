import sys
import logging

from urllib.parse import urlparse

from PyQt5.QtCore import QCoreApplication, QThreadPool, pyqtSlot

from terramirror.directory_list_analyser import DirectoryListWorker
from terramirror.download_analyser import DownloadAnalyser
from terramirror.job_info import JobInfo
from terramirror.instructions import Instruction
from terramirror.payload import AnalyseIndexPayload


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
        self._urls_queued = set()

    def _enqueue_directory_list_analysis(self, url):
        job_info = JobInfo(
            Instruction.ANALYSE_DIRECTORY_LIST,
            AnalyseIndexPayload(url)
        )
        worker = DirectoryListWorker(job_info, self._config)
        worker.signals.finished.connect(self.handle_finished_job)
        worker.signals.enqueue_directory_list_analysis.connect(self.enqueue_directory_list_analysis)
        worker.signals.enqueue_download_analysis.connect(self.enqueue_download_analysis)
        worker.signals.enqueue_small_download.connect(self.enqueue_small_download)
        # Execute
        self.threadpool.start(worker)

    @pyqtSlot(str)
    def enqueue_download_analysis(self, url: str):
        logging.info(f"enqueue_download_analysis recieved with {url}")
        if self._validate_url(url):
            logging.info(f"URL {url} passed validation, queuing")
            self._job_count += 1
            self._total_jobs += 1
            job_info = JobInfo(
                Instruction.ANALYSE_DIRECTORY_LIST,
                AnalyseIndexPayload(url)
            )
            worker = DownloadAnalyser(job_info, self._config)
            worker.signals.finished.connect(self.handle_finished_job)
            worker.signals.enqueue_small_download.connect(self.enqueue_small_download)
            worker.signals.enqueue_large_download.connect(self.enqueue_small_download)
            # Execute
            self.threadpool.start(worker)

    @pyqtSlot(str)
    def enqueue_small_download(self, url: str):
        self._job_count += 1
        self._total_jobs += 1

    @pyqtSlot(str)
    def enqueue_directory_list_analysis(self, url: str):
        logging.info(f"enqueue_directory_list_analysis recieved with {url}")

        if self._validate_url(url):
            logging.info(f"URL {url} passed validation, queuing")
            self._job_count += 1
            self._total_jobs += 1
            self._enqueue_directory_list_analysis(url)

    def _validate_url(self, url):
        logging.debug(f"Validaing url {url}")
        if url in self._urls_queued:
            logging.debug(f"Not queuing already seen url {url}")
            return False

        self._urls_queued.add(url)

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
        print(f"Handle_Finished recieved job info: {job_info}")
        print(f"Job count: {self._job_count} Active thread count: {self.threadpool.activeThreadCount()}")

        if self._job_count == 0:
            print("All done!")
            self.exit(0)

        if self._total_jobs >= 10000:
            print("Exit for test!")
            self.threadpool.clear()
            self.exit(0)


if __name__ == "__main__":
    import sys
    main = Main(sys.argv)
    sys.exit(main.exec_())

