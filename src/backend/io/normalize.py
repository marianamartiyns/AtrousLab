from __future__ import annotations
import numpy as np

def abs_then_hist_expand(x: np.ndarray) -> np.ndarray:
    """
    NORMALIZAÇÃO PARA VISUALIZAÇÃO (ordem obrigatória):
      1) abs
      2) expansão min-max para [0,255]

    Entrada: matriz (float/int) com qualquer faixa, pode ter negativos.
    Saída: uint8 em [0,255].
    """
    # 1) ABS (obrigatório vir antes)
    x_abs = np.abs(x.astype(np.float32, copy=False))

    # 2) EXPANSÃO (min-max) para [0,255]
    x_min = float(np.min(x_abs))
    x_max = float(np.max(x_abs))

    if x_max == x_min:
        return np.zeros_like(x_abs, dtype=np.uint8)

    y = (x_abs - x_min) * (255.0 / (x_max - x_min))
    y = np.clip(np.rint(y), 0, 255).astype(np.uint8)
    return y


def to_uint8_clipped(x: np.ndarray) -> np.ndarray:
    """
    Útil para salvar imagens que já estão em 0..255 (sem normalizar).
    Clipa e converte para uint8.
    """
    y = np.clip(x, 0, 255)
    return np.rint(y).astype(np.uint8)