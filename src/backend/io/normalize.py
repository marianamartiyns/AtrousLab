from __future__ import annotations

import numpy as np


class NormalizeError(Exception):
    pass


def abs_then_hist_expand(x: np.ndarray) -> np.ndarray:
    """
    Normalização para visualização:
      1) abs
      2) expansão min-max para [0,255]

    Entrada:
      - matriz 2D com valores float/int

    Saída:
      - matriz 2D uint8
    """
    if not isinstance(x, np.ndarray):
        raise NormalizeError("x deve ser np.ndarray.")

    if x.ndim != 2:
        raise NormalizeError(f"Esperado array 2D. Obtido: {x.ndim}D.")

    x_abs = np.abs(x.astype(np.float32, copy=False))

    x_min = float(np.min(x_abs))
    x_max = float(np.max(x_abs))

    if x_max == x_min:
        return np.zeros_like(x_abs, dtype=np.uint8)

    y = (x_abs - x_min) * (255.0 / (x_max - x_min))
    y = np.clip(np.rint(y), 0, 255).astype(np.uint8)
    return y


def to_uint8_clipped(x: np.ndarray) -> np.ndarray:
    """
    Clipa para [0,255], arredonda e converte para uint8.
    """
    if not isinstance(x, np.ndarray):
        raise NormalizeError("x deve ser np.ndarray.")

    y = np.clip(x, 0, 255)
    return np.rint(y).astype(np.uint8)