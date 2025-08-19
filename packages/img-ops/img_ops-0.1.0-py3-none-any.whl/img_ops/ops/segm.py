from __future__ import annotations

__all__ = ["find_contours", "connected_components"]

from ..types import CvImage
from ..enums import ComputeDevice
from ..registry import dispatch

def find_contours(mask: CvImage, mode: int, method: int):
    """
        Поиск контуров на бинарной маске (CPU-only).
        Args:
            mask: бинарная маска.
            mode: режим поиска (см. cv2.RETR_*).
            method: метод аппроксимации (см. cv2.CHAIN_*).

        Returns:
            (contours, hierarchy) — как в cv2.findContours.
    """
    return dispatch("find_contours", ComputeDevice.CPU, mask, mode, method)

def connected_components(mask: CvImage):
    """
        Поиск связных компонент (CPU-only).
        Args:
            mask: бинарная маска uint8.
        Returns:
            (num_labels, labels, stats)
            Совместимо с прежним кодом: centroids отбрасываются.
            Если понадобятся центроиды — сделаем отдельную функцию.
    """
    num_labels, labels, stats, _centroids = dispatch("connected_components", ComputeDevice.CPU, mask)
    return num_labels, labels, stats
