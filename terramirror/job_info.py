from dataclasses import dataclass
import typing

from terramirror.instructions import Instruction
from terramirror.payload import AnalyseIndexPayload

@dataclass()
class JobInfo():
    instruction: Instruction
    payload: typing.Type[AnalyseIndexPayload]