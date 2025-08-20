from __future__ import annotations

from enum import StrEnum
from typing import Literal


class TaskChoice(StrEnum):
    """Enum for task choices."""

    CPU = "cpu"
    MEM = "mem"
    DISK = "disk"
    GPU = "gpu"


CPU = TaskChoice.CPU
MEM = TaskChoice.MEM
DISK = TaskChoice.DISK
GPU = TaskChoice.GPU

CPU_MEM: tuple[Literal[TaskChoice.CPU], Literal[TaskChoice.MEM]] = (CPU, MEM)
CPU_MEM_GPU: tuple[Literal[TaskChoice.CPU], Literal[TaskChoice.MEM], Literal[TaskChoice.GPU]] = (CPU, MEM, GPU)
ALL_TASKS: tuple[
    Literal[TaskChoice.CPU],
    Literal[TaskChoice.MEM],
    Literal[TaskChoice.DISK],
    Literal[TaskChoice.GPU],
] = (CPU, MEM, DISK, GPU)
