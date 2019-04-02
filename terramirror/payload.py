from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class AnalyseIndexPayload:
    url: str


@dataclass
class AnalyseDownloadPayload(AnalyseIndexPayload):
    pass


@dataclass
class DownloadSmallFilePayload(AnalyseIndexPayload):
    destination: Path
    download_datetime: datetime
    download_size: int


@dataclass
class DownloadLargeFilePayload(DownloadSmallFilePayload):
    pass
