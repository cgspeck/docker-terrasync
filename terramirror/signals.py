from datetime import datetime
from pathlib import Path

from terramirror.job_info import JobInfo
from PyQt5.QtCore import QObject, pyqtSignal


class WorkerSignals(QObject):
    finished = pyqtSignal(
        JobInfo,
        name='finished',
        arguments=['Jobinfo Dataclass']
    )

    failed = pyqtSignal(
        JobInfo, Exception,
        name='failed',
        arguments=['Jobinfo Dataclass', 'Exception that was caught']
    )


    enqueue_download_analysis = pyqtSignal(
        str,
        name='enqueueDownloadAnalysis',
        arguments=['URL of download to analyise']
    )

    enqueue_small_download = pyqtSignal(
        str, Path, int, datetime,
        name='enqueueSmallDownload',
        arguments=['Download URL', 'Destination Path', 'Download Size', 'Download Datetime']
    )

    enqueue_large_download = pyqtSignal(
        str, Path, int, datetime,
        name='enqueueLargeDownload',
        arguments=['Download URL', 'Destination Path', 'Download Size', 'Download Datetime']
    )

    enqueue_directory_list_analysis = pyqtSignal(
        str,
        name='enqueueDirectoryListAnalysis',
        arguments=['URL of directory list to analyse']
    )
