from pathlib import Path
from dataclasses import dataclass


@dataclass()
class Config:
    destination: Path
    mirror: str = None
    large_download_threshold: int = 104857600  # 100 mb

    @property
    def headers(self):
        return { 'user-agent': 'terramirror/0.0.1' }
