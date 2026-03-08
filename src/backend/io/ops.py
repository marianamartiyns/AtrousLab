from __future__ import annotations

from typing import Tuple
import numpy as np

from .image_io import ImageShapeError


def assert_rgb_hwc(data: np.ndarray) -> None:
    if not isinstance(data, np.ndarray):
        raise ImageShapeError("data deve ser np.ndarray.")
    if data.ndim != 3 or data.shape[2] != 3:
        raise ImageShapeError(f"Esperado H x W x 3. Obtido: {getattr(data, 'shape', None)}")


def get_pixel(data: np.ndarray, y: int, x: int) -> Tuple[int, int, int]:
    """
    Retorna o pixel (y, x) no formato (R, G, B).
    """
    assert_rgb_hwc(data)

    h, w, _ = data.shape
    if not (0 <= y < h and 0 <= x < w):
        raise IndexError(f"Pixel fora da imagem: (y={y}, x={x}) em H={h}, W={w}")

    r, g, b = data[y, x]
    return int(r), int(g), int(b)


def set_pixel(data: np.ndarray, y: int, x: int, rgb: Tuple[int, int, int]) -> None:
    """
    Define o pixel (y, x) com clip para [0,255].
    """
    assert_rgb_hwc(data)

    h, w, _ = data.shape
    if not (0 <= y < h and 0 <= x < w):
        raise IndexError(f"Pixel fora da imagem: (y={y}, x={x}) em H={h}, W={w}")

    r, g, b = rgb
    data[y, x, 0] = np.uint8(np.clip(int(r), 0, 255))
    data[y, x, 1] = np.uint8(np.clip(int(g), 0, 255))
    data[y, x, 2] = np.uint8(np.clip(int(b), 0, 255))


def split_channels(data: np.ndarray, as_float: bool = True) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Separa H x W x 3 em canais R, G, B.

    - as_float=True  -> float32
    - as_float=False -> mantém dtype original
    """
    assert_rgb_hwc(data)

    if as_float:
        arr = data.astype(np.float32, copy=False)
        return arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]

    return data[:, :, 0], data[:, :, 1], data[:, :, 2]


def merge_channels(
    r: np.ndarray,
    g: np.ndarray,
    b: np.ndarray,
    clip: bool = True
) -> np.ndarray:
    """
    Recombina canais 2D em imagem H x W x 3.

    - clip=True  -> clipa e converte para uint8
    - clip=False -> exige canais uint8
    """
    if not (isinstance(r, np.ndarray) and isinstance(g, np.ndarray) and isinstance(b, np.ndarray)):
        raise ImageShapeError("r, g, b devem ser np.ndarray.")

    if r.shape != g.shape or r.shape != b.shape:
        raise ImageShapeError(f"Shapes diferentes: r={r.shape}, g={g.shape}, b={b.shape}")

    if r.ndim != 2:
        raise ImageShapeError(f"Esperado canais 2D (H x W). Obtido: {r.ndim}D")

    if clip:
        r8 = np.clip(np.rint(r), 0, 255).astype(np.uint8)
        g8 = np.clip(np.rint(g), 0, 255).astype(np.uint8)
        b8 = np.clip(np.rint(b), 0, 255).astype(np.uint8)
    else:
        if r.dtype != np.uint8 or g.dtype != np.uint8 or b.dtype != np.uint8:
            raise ImageShapeError("clip=False exige r, g, b uint8.")
        r8, g8, b8 = r, g, b

    return np.stack([r8, g8, b8], axis=2)