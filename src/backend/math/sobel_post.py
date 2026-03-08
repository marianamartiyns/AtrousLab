from __future__ import annotations

import numpy as np


class PostProcessError(Exception):
    pass


def sobel_visualize_channel(x: np.ndarray) -> np.ndarray:
    """
    Pós-processamento Sobel para um canal:

    1) valor absoluto
    2) min e max
    3) expansão linear para [0, 255]

    Entrada: matriz 2D
    Saída: matriz 2D uint8
    """
    if not isinstance(x, np.ndarray):
        raise PostProcessError("Entrada deve ser np.ndarray.")

    if x.ndim != 2:
        raise PostProcessError(f"Esperado matriz 2D. Obtido: {x.ndim}D.")

    x_abs = np.abs(x.astype(np.float32, copy=False))

    min_val = float(np.min(x_abs))
    max_val = float(np.max(x_abs))

    if max_val == min_val:
        return np.zeros_like(x_abs, dtype=np.uint8)

    y = (x_abs - min_val) * (255.0 / (max_val - min_val))
    y = np.clip(np.rint(y), 0, 255).astype(np.uint8)

    return y


def sobel_visualize_rgb(
    r: np.ndarray,
    g: np.ndarray,
    b: np.ndarray,
) -> np.ndarray:

    # Aplica o pós-processamento Sobel em cada canal e retorna imagem RGB H x W x 3 uint8.
    r_vis = sobel_visualize_channel(r)
    g_vis = sobel_visualize_channel(g)
    b_vis = sobel_visualize_channel(b)

    return np.stack([r_vis, g_vis, b_vis], axis=2)