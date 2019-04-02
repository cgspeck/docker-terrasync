from terramirror.job_info import
from PyQt5.QtCore import QObject, pyqtSignal

class WorkerSignals(QObject):
    finished = pyqtSignal()
