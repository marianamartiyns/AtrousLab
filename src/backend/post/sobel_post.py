from __future__ import annotations
import numpy as np
from typing import Tuple
from .errors import PostProcessError


def sobel_visualize_channel(x: np.ndarray) -> np.ndarray:
    """
    Pós-processamento específico para Sobel (1 canal):

      1) abs
      2) calcular min e max
      3) expansão linear para [0,255]

    Entrada: matriz 2D float/int
    Saída: matriz 2D uint8
    """

    if not isinstance(x, np.ndarray):
        raise PostProcessError("Entrada deve ser np.ndarray")

    if x.ndim != 2:
        raise PostProcessError(f"Esperado matriz 2D. Obtido: {x.ndim}D")

    # 1️⃣ ABS (obrigatório primeiro)
    x_abs = np.abs(x.astype(np.float32, copy=False))

    # 2️⃣ min e max
    min_val = float(np.min(x_abs))
    max_val = float(np.max(x_abs))

    # 3️⃣ expansão linear
    if max_val == min_val:
        return np.zeros_like(x_abs, dtype=np.uint8)

    y = (x_abs - min_val) * (255.0 / (max_val - min_val))
    y = np.clip(np.rint(y), 0, 255).astype(np.uint8)

    return y


def sobel_visualize_rgb(
    r: np.ndarray,
    g: np.ndarray,
    b: np.ndarray
) -> np.ndarray:
    """
    Aplica o pós-processamento Sobel em cada canal
    e retorna RGB uint8 H×W×3
    """

    r_vis = sobel_visualize_channel(r)
    g_vis = sobel_visualize_channel(g)
    b_vis = sobel_visualize_channel(b)

    return np.stack([r_vis, g_vis, b_vis], axis=2)