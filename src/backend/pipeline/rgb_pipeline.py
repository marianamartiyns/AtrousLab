from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Literal, Tuple
import numpy as np

from src.backend.io.ops import split_channels, merge_channels, assert_rgb_hwc
from src.backend.math import correlate2d_dilated_stride
from src.backend.activation import apply_activation
from src.backend.io.normalize import abs_then_hist_expand 

class PipelineError(Exception):
    pass

ActivationType = Literal["relu", "identity"]

@dataclass(frozen=True)
class RGBPipelineResult:
    """
    - out_r/g/b: resultado por canal (float32) após correlação + ativação
    - out_rgb_u8: recombinação RGB pronta para salvar (uint8)
    - vis_rgb_u8: opcional, versão para VISUALIZAÇÃO (abs -> hist expand) (uint8)
    """
    out_r: np.ndarray
    out_g: np.ndarray
    out_b: np.ndarray
    out_rgb_u8: np.ndarray
    vis_rgb_u8: Optional[np.ndarray] = None


def run_rgb_pipeline(
    rgb_u8: np.ndarray,
    mask: list[list[float]] | np.ndarray,
    r: int,
    stride: int,
    activation: ActivationType,
    make_visualization: bool = False,
) -> RGBPipelineResult:
    """
    Pipeline RGB:
      1) separa R,G,B
      2) aplica correlação por canal (sem padding, com dilatação r e stride)
      3) aplica ativação após o somatório
      4) recombina

    Entradas:
      - rgb_u8: H×W×3 uint8
      - mask: m×n (list ou np.ndarray)
      - r: 1..5
      - stride: 1..5
      - activation: 'relu' ou 'identity'
      - make_visualization: se True, gera vis_rgb_u8 por abs->hist_expand (por canal)

    Saídas:
      - canais float32 (out_r,out_g,out_b)
      - out_rgb_u8 (uint8, clip)
      - vis_rgb_u8 (uint8) se solicitado
    """
    try:
        assert_rgb_hwc(rgb_u8)
    except Exception as e:
        raise PipelineError(f"Entrada rgb_u8 inválida: {e}") from e

    if rgb_u8.dtype != np.uint8:
        raise PipelineError(f"rgb_u8 deve ser uint8. Obtido: {rgb_u8.dtype}")

    # 1) separa canais em float32 para permitir negativos no processamento
    r_in, g_in, b_in = split_channels(rgb_u8, as_float=True)

    # 2) correlação por canal
    r_corr = correlate2d_dilated_stride(r_in, mask, r=r, stride=stride)
    g_corr = correlate2d_dilated_stride(g_in, mask, r=r, stride=stride)
    b_corr = correlate2d_dilated_stride(b_in, mask, r=r, stride=stride)

    # 3) ativação após somatório
    r_out = apply_activation(r_corr, activation)
    g_out = apply_activation(g_corr, activation)
    b_out = apply_activation(b_corr, activation)

    # 4) recombina (clip para salvar em RGB 24 bits)
    out_rgb_u8 = merge_channels(r_out, g_out, b_out, clip=True)

    vis_rgb_u8 = None
    if make_visualization:
        # Visualização: 1) abs 2) hist expand (ordem obrigatória)
        r_vis = abs_then_hist_expand(r_out)
        g_vis = abs_then_hist_expand(g_out)
        b_vis = abs_then_hist_expand(b_out)
        vis_rgb_u8 = np.stack([r_vis, g_vis, b_vis], axis=2)

    return RGBPipelineResult(
        out_r=r_out,
        out_g=g_out,
        out_b=b_out,
        out_rgb_u8=out_rgb_u8,
        vis_rgb_u8=vis_rgb_u8,
    )