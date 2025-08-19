from __future__ import annotations

__all__ = ['CvImage', 'PointHSV']

from typing import TypeAlias, Union
import numpy as np
from numpy.typing import NDArray

#: 8-битное изображение (обычно BGR) или float32.
#: Допускаем (H, W, 3) и (H, W); форму не фиксируем типами.
CvImage: TypeAlias = NDArray[Union[np.uint8, np.float32]]

#: Точка/порог в HSV как (H, S, V).
PointHSV: TypeAlias = tuple[int, int, int]
