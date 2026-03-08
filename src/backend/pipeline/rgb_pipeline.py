from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Literal
import numpy as np
from src.backend.io.ops import split_channels, merge_channels, assert_rgb_hwc
from src.backend.math.correlation2d import correlate2d_dilated_stride
from src.backend.activation.activations import apply_activation
from src.backend.io.normalize import abs_then_hist_expand


class PipelineError(Exception):
    pass


ActivationType = Literal["relu", "identity"]


@dataclass(frozen=True)
class RGBPipelineResult:
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
      1) separa R, G, B
      2) aplica correlação dilatada por canal
      3) aplica ativação após o somatório
      4) recombina em RGB

    Entradas:
      - rgb_u8: H x W x 3 uint8
      - mask: m x n
      - r: 1..5
      - stride: 1..5
      - activation: 'relu' ou 'identity'
      - make_visualization: gera imagem para visualização por canal
    """
    try:
        assert_rgb_hwc(rgb_u8)
    except Exception as e:
        raise PipelineError(f"Entrada rgb_u8 inválida: {e}") from e

    if rgb_u8.dtype != np.uint8:
        raise PipelineError(f"rgb_u8 deve ser uint8. Obtido: {rgb_u8.dtype}")

    act = str(activation).strip().lower()
    if act not in {"relu", "identity"}:
        raise PipelineError(f"Ativação inválida: {activation}")

    # separa canais
    r_in, g_in, b_in = split_channels(rgb_u8, as_float=True)

    # correlação por canal
    r_corr = correlate2d_dilated_stride(r_in, mask=mask, r=r, stride=stride)
    g_corr = correlate2d_dilated_stride(g_in, mask=mask, r=r, stride=stride)
    b_corr = correlate2d_dilated_stride(b_in, mask=mask, r=r, stride=stride)

    # ativação após o somatório
    r_out = apply_activation(r_corr, act)
    g_out = apply_activation(g_corr, act)
    b_out = apply_activation(b_corr, act)

    # saída RGB uint8
    out_rgb_u8 = merge_channels(r_out, g_out, b_out, clip=True)

    vis_rgb_u8 = None
    if make_visualization:
        r_vis = abs_then_hist_expand(r_out)
        g_vis = abs_then_hist_expand(g_out)
        b_vis = abs_then_hist_expand(b_out)
        vis_rgb_u8 = merge_channels(r_vis, g_vis, b_vis, clip=False)

    return RGBPipelineResult(
        out_r=r_out,
        out_g=g_out,
        out_b=b_out,
        out_rgb_u8=out_rgb_u8,
        vis_rgb_u8=vis_rgb_u8,
    )