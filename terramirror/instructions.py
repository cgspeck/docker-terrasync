from enum import Enum, unique

@unique
class Instruction(Enum):
    ANALYSE_DIRECTORY_LIST = 0
    ANALYSE_DOWNLOAD_CANDIDATE = 1
    DOWNLOAD_SMALL_FILE = 2
    DOWNLOAD_LARGE_FILE = 3