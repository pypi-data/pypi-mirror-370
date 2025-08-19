from __future__ import annotations

__all__ = ["ImageProcessor"]

from typing import Tuple
from .types import CvImage, PointHSV
from .enums import ComputeDevice
from .device import resolve_device
from .ops import color, filters, segm

class ImageProcessor:
    """
        Экземплярный фасад с дефолтным устройством исполнения.
        Логика:
        - Если в вызове метода `device` не указан — берём `default_device` из конструктора.
        - Если `device` указан — используем его (локальный override).
        - Если выбранное устройство недоступно — операция прозрачно выполнится на CPU.
        Пример:
            proc = ImageProcessor(default_device="gpu")
            hsv = proc.bgr_to_hsv(img)                     # выполнится на GPU (если доступно)
            blur = proc.gauss_blur(img, (5,5), 1.2, device="cpu")  # override -> CPU
    """

    def __init__(self, default_device: str | ComputeDevice = "cpu"):
        """
            Args:
                default_device: "cpu" | "gpu" | "mps" | ComputeDevice.
        """
        self.default_device: ComputeDevice = resolve_device(default_device, ComputeDevice.CPU)

    # ---------- служебное ----------

    def _effective_device(self, device: str | ComputeDevice | None) -> ComputeDevice:
        """
            Возвращает итоговое устройство: либо override из аргумента,
            либо default из конструктора.
        """
        return resolve_device(device, self.default_device)

    # ---------- color ----------

    def bgr_to_rgb(self, image: CvImage, device: str | ComputeDevice | None = None) -> CvImage:
        """ Конвертирует изображение BGR -> RGB. """
        return color.bgr_to_rgb(image,
                                        device=self._effective_device(device),
                                        default=self.default_device)

    def rgb_to_bgb(self, image: CvImage, device: str | ComputeDevice | None = None) -> CvImage:
        """ Конвертирует изображение RGB -> BGR. """
        return color.rgb_to_bgr(image,
                                        device=self._effective_device(device),
                                        default=self.default_device)

    def bgr_to_hsv(self, image: CvImage, device: str | ComputeDevice | None = None) -> CvImage:
        """ Конвертирует изображение BGR -> HSV. """
        return color.bgr_to_hsv(image,
                                        device=self._effective_device(device),
                                        default=self.default_device)

    def in_range(self, image_hsv: CvImage, lower: PointHSV, upper: PointHSV,
                 device: str | ComputeDevice | None = None) -> CvImage:
        """
            Пороговая фильтрация в HSV-цветовом пространстве.
            Args:
                image_hsv: изображение в HSV.
                lower: нижняя граница (H, S, V).
                upper: верхняя граница (H, S, V).
        """
        return color.in_range(image_hsv, lower, upper,
                              device=self._effective_device(device),
                              default=self.default_device)

    # ---------- filters ----------

    def gauss_blur(self, image: CvImage, ksize: Tuple[int, int], sigma: float,
                   device: str | ComputeDevice | None = None) -> CvImage:
        """ Гауссово размытие. """
        return filters.gauss_blur(image, ksize, sigma,
                                  device=self._effective_device(device),
                                  default=self.default_device)

    # ---------- segmentation ----------

    def find_contours(self, mask: CvImage, mode: int, method: int):
        """ Поиск контуров на бинарной маске (CPU-only). """
        return segm.find_contours(mask, mode, method)

    def connected_components(self, mask: CvImage):
        """
            Поиск связных компонент (CPU-only).
            Returns:
                (num_labels, labels, stats)
                Примечание: centroids опущены для простоты API.
        """
        return segm.connected_components(mask)
