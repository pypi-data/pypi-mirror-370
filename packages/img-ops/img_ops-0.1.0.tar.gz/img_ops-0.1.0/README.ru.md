# ImageOperations

**ImageOperations** — минимальная библиотека операций над изображениями с учётом устройства
(CPU/GPU/MPS-заглушка). Можно вызывать функции **без инициализации**, либо пользоваться небольшим
фасадом с **устройством по умолчанию**. Если нужное устройство недоступно — библиотека
**прозрачно переключается на CPU**.

- ✅ Функциональный и объектный API
- ✅ Выбор устройства в каждом вызове (`device="cpu"|"gpu"|"mps"`)
- ✅ Безопасный фолбэк (GPU/MPS → CPU)
- ✅ Типы (PEP 561, `py.typed`)
- ✅ Чистая модульная структура (`ops/`, `registry`, `device`, `types`)
- 🔧 Легко расширять: добавляйте операции и бэкенды без изменения публичного API

> **Примечание:** MPS (Apple Metal) зарезервирован в `ComputeDevice`, но сейчас всегда падает на CPU.

---

## Установка

```bash
poetry add img-ops
# или pip:
# pip install img-ops
```

**Headless-окружения:** замените `opencv-python` на `opencv-python-headless`, если не нужны GUI-функции.

---

## Быстрый старт

### Функциональный API

```python
from img_ops import convert_bgr_to_hsv, in_range, gauss_blur, ComputeDevice

hsv = convert_bgr_to_hsv(img, device="gpu")  # если есть CUDA; иначе CPU
mask = in_range(hsv, (0, 80, 80), (10, 255, 255))  # по умолчанию CPU
blur = gauss_blur(img, (5, 5), 1.2, device=ComputeDevice.CPU)
```

### Экземпляр с устройством по умолчанию

```python
from img_ops import ImageProcessor

proc = ImageProcessor(default_device="gpu")
hsv = proc.convert_bgr_to_hsv(img)  # GPU (фолбэк → CPU)
mask = proc.in_range(hsv, (0, 80, 80), (10, 255, 255))  # использует default_device
blur = proc.gauss_blur(img, (5, 5), 1.2, device="cpu")  # локальный override → CPU
```

---

## Поддерживаемые операции (начальный набор)

- **Цвет:** `convert_bgr_to_rgb`, `convert_bgr_to_hsv`, `in_range`
- **Фильтры:** `gauss_blur`
- **Сегментация (только CPU):** `find_contours`, `connected_components`
- **Утилиты:** `sum_masks` (внутренний реестр)

Новые операции добавляются через `registry.py` + тонкие обёртки в `ops/`.

---

## Устройства

```python
from img_ops import ComputeDevice
# ComputeDevice.GPU  -> CUDA (если доступна)
# ComputeDevice.MPS  -> зарезервировано (фолбэк на CPU)
# ComputeDevice.CPU  -> всегда доступен
```

### Поведение фолбэка
- Запросили `GPU`, но CUDA недоступна → автоматический фолбэк на `CPU`.
- `MPS` пока всегда фолбэк на `CPU` (плейсхолдер).

---

## Типы

Пакет поставляет типы и `py.typed`.

```python
from img_ops import CvImage, PointHSV

# CvImage: NDArray[uint8 | float32]  # форма (H,W,3) или (H,W)
# PointHSV: tuple[int, int, int]     # (H, S, V)
```

Форму (shape) типами не фиксируем — придерживаемся соглашений.

---

## Обработка ошибок

- Неизвестное устройство → `ValueError` со списком допустимых значений.
- Нет реализации даже на CPU → `NotImplementedError` (после попытки фолбэка).

---

## Расширение библиотеки

### Добавить новую операцию
1. Реализовать CPU/GPU/MPS-варианты в `registry.py` (`_cpu()`, `_gpu()`, `_mps()`).
2. Создать тонкую обёртку в `ops/<category>.py` с нормализацией `device` и вызовом `dispatch(...)`.
3. (Опционально) Экспортировать в `ops/__init__.py` и корневом `__init__.py`.

### Добавить новое устройство
1. Расширить `ComputeDevice` (например, `OPENCL`, `TORCH`).
2. Добавить сборщик реестра (`_opencl()`), подключить к `REGISTRY`.
3. Добавить проверки доступности в `device.py` и нормализацию в `ops/*.py`.

---

## Производительность

- GPU полезен на больших изображениях/тяжёлых ядрах; на мелких кадрах CPU может быть быстрее из‑за
  накладных расходов upload/download.
- Для сложения масок предпочтительнее `cv2.add`, а не `a + b` (корректная сатурация).

---

## Тестирование

```bash
poetry run pytest
poetry run mypy src/img_ops
poetry run ruff check .
```

---

## Author

[![Telegram](https://img.shields.io/badge/-Telegram-26A5E4?style=flat&logo=telegram&logoColor=white)](https://t.me/omigutin)
[![GitHub](https://img.shields.io/badge/-GitHub-181717?style=flat&logo=github&logoColor=white)](https://github.com/omigutin)

**Ссылка на проект:** <https://github.com/omigutin/img_ops>
**Ссылка на проектные работы:** <ttps://github.com/users/omigutin/projects/4>
**Контакт:** [migutin83@yandex.ru](mailto:migutin83@yandex.ru)

---

## Лицензия

MIT — см. [LICENSE](LICENSE).
