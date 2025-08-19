from __future__ import annotations

__all__ = ['ComputeDevice']

from enum import Enum

class ComputeDevice(Enum):
    """
        Устройство исполнения операций.
        GPU — CUDA (cv2.cuda.*), если доступно.
        MPS — резерв под Apple Metal (пока фолбэк на CPU).
        CPU — процессор (всегда доступен).
    """
    GPU = 'gpu'
    MPS = 'mps'
    CPU = 'cpu'
