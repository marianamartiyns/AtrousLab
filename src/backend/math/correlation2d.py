from __future__ import annotations
from typing import List, Tuple
import numpy as np

class MathError(Exception):
    pass

class CorrelationShapeError(MathError):
    pass

class CorrelationParamError(MathError):
    pass


def kernel_effective_size(mask: List[List[float]] | np.ndarray, r: int) -> Tuple[int, int]:
    """
    Para máscara m×n e dilatação r:
      k_eff_h = (m - 1) * r + 1
      k_eff_w = (n - 1) * r + 1
    """
    m, n = _mask_shape(mask)
    _validate_r(r)
    k_eff_h = (m - 1) * r + 1
    k_eff_w = (n - 1) * r + 1
    return k_eff_h, k_eff_w


def output_size_no_padding(H: int, W: int, mask: List[List[float]] | np.ndarray, r: int, stride: int) -> Tuple[int, int]:
    """
    Sem padding:
      H_out = floor((H - k_eff_h)/stride) + 1, se H >= k_eff_h, senão 0
      W_out = floor((W - k_eff_w)/stride) + 1, se W >= k_eff_w, senão 0
    """
    _validate_stride(stride)
    k_eff_h, k_eff_w = kernel_effective_size(mask, r)

    if H < k_eff_h or W < k_eff_w:
        return 0, 0

    H_out = ((H - k_eff_h) // stride) + 1
    W_out = ((W - k_eff_w) // stride) + 1
    return int(H_out), int(W_out)


def correlate2d_dilated_stride(
    x: np.ndarray,
    mask: List[List[float]] | np.ndarray,
    r: int,
    stride: int,
) -> np.ndarray:
    """
    Correlação 2D (não é convolução):
      y[out_y, out_x] = sum_{i,j} x[in_y + i*r, in_x + j*r] * mask[i,j]
    onde:
      in_y = out_y * stride
      in_x = out_x * stride

    - x: matriz 2D (H×W), float/int
    - mask: matriz m×n (float/int), retangular
    - r: dilatação (1..5)
    - stride: passo (1..5)
    - sem padding (somente posições válidas)
    """
    if not isinstance(x, np.ndarray) or x.ndim != 2:
        raise CorrelationShapeError(f"x deve ser np.ndarray 2D (H×W). Obtido: {getattr(x, 'shape', None)}")

    _validate_r(r)
    _validate_stride(stride)

    mask_arr = _mask_to_array(mask)  # m×n float32
    m, n = mask_arr.shape
    H, W = x.shape

    # tamanhos efetivos do kernel dilatado
    k_eff_h = (m - 1) * r + 1
    k_eff_w = (n - 1) * r + 1

    # saída (sem padding)
    H_out, W_out = output_size_no_padding(H, W, mask_arr, r, stride)
    out = np.zeros((H_out, W_out), dtype=np.float32)

    x_f = x.astype(np.float32, copy=False)

    # Loop manual
    for oy in range(H_out):
        in_y = oy * stride
        for ox in range(W_out):
            in_x = ox * stride

            acc = 0.0
            # somatório ponderado com dilatação r
            for i in range(m):
                yy = in_y + i * r
                for j in range(n):
                    xx = in_x + j * r
                    acc += x_f[yy, xx] * mask_arr[i, j]

            out[oy, ox] = acc

    return out



# Helpers + validação
def _validate_r(r: int) -> None:
    if not isinstance(r, int) or isinstance(r, bool):
        raise CorrelationParamError("r deve ser int.")
    if r < 1 or r > 5:
        raise CorrelationParamError(f"r fora do intervalo 1–5: {r}")

def _validate_stride(stride: int) -> None:
    if not isinstance(stride, int) or isinstance(stride, bool):
        raise CorrelationParamError("stride deve ser int.")
    if stride < 1 or stride > 5:
        raise CorrelationParamError(f"stride fora do intervalo 1–5: {stride}")

def _mask_shape(mask: List[List[float]] | np.ndarray) -> Tuple[int, int]:
    if isinstance(mask, np.ndarray):
        if mask.ndim != 2:
            raise CorrelationShapeError(f"mask deve ser 2D. Obtido: {mask.ndim}D")
        m, n = mask.shape
        if m == 0 or n == 0:
            raise CorrelationShapeError("mask não pode ser vazia.")
        return int(m), int(n)

    # lista de listas
    if not isinstance(mask, list) or len(mask) == 0:
        raise CorrelationShapeError("mask deve ser uma lista de listas não vazia.")
    if not all(isinstance(row, list) and len(row) > 0 for row in mask):
        raise CorrelationShapeError("mask deve ser lista de listas com linhas não vazias.")

    n = len(mask[0])
    for i, row in enumerate(mask):
        if len(row) != n:
            raise CorrelationShapeError(f"mask deve ser retangular: linha {i} tem {len(row)} colunas, esperado {n}.")
    return len(mask), n

def _mask_to_array(mask: List[List[float]] | np.ndarray) -> np.ndarray:
    m, n = _mask_shape(mask)

    if isinstance(mask, np.ndarray):
        arr = mask.astype(np.float32, copy=False)
    else:
        try:
            arr = np.array(mask, dtype=np.float32)
        except Exception as e:
            raise CorrelationShapeError(f"Falha ao converter mask para array float32: {e}") from e

    if arr.shape != (m, n):
        raise CorrelationShapeError(f"mask shape inesperado após conversão: {arr.shape}, esperado {(m, n)}")

    return arr