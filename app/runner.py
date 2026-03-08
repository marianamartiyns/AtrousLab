from __future__ import annotations
from pathlib import Path
from typing import Any
import re
import numpy as np
from src.backend.config.config import load_config_from_uploads
from src.backend.io.image_io import read_rgb24, write_rgb24
from src.backend.io.models import RGBImage
from src.backend.pipeline.rgb_pipeline import run_rgb_pipeline
from src.backend.math.sobel_post import sobel_visualize_rgb
from app.settings import OUTPUT_DIR


class RunnerError(Exception):
    pass


def _read_bytes(path: Path) -> bytes:
    try:
        return path.read_bytes()
    except Exception as e:
        raise RunnerError(f"Falha ao ler arquivo: {path}. Erro: {e}") from e


def _safe_stem(filename: str) -> str:
    # ajuste nome do arquivo: remover extensão e espaços, e substituir caracteres não alfanuméricos por '_'
    stem = Path(filename).stem.strip()
    stem = stem.replace(" ", "_")
    stem = re.sub(r"[^A-Za-z0-9_\-]+", "", stem)
    return stem or "mask"


def run_pipeline(
    *,
    config_path: Path,
    mask_path: Path,
    image_path: Path,
    run_id: str,
) -> dict[str, Any]:
    config_bytes = _read_bytes(config_path)
    mask_bytes = _read_bytes(mask_path)

    cfg = load_config_from_uploads(
        config_bytes=config_bytes,
        config_name=config_path.name,
        mask_bytes=mask_bytes,
        mask_name=mask_path.name,
    )

    rgb_image = read_rgb24(image_path)

    pipeline_result = run_rgb_pipeline(
        rgb_u8=rgb_image.data,
        mask=cfg.mask,
        r=cfg.r,
        stride=cfg.stride,
        activation=cfg.activation,
        make_visualization=False,
    )

    output_rgb_u8: np.ndarray

    if cfg.filter_type == "sobel":
        output_rgb_u8 = sobel_visualize_rgb(
            pipeline_result.out_r,
            pipeline_result.out_g,
            pipeline_result.out_b,
        )
    else:
        output_rgb_u8 = pipeline_result.out_rgb_u8

    mask_base_name = _safe_stem(cfg.mask_name)
    output_filename = f"{mask_base_name}_output_{run_id}.png"
    output_path = OUTPUT_DIR / output_filename

    out_image = RGBImage(path=str(output_path), data=output_rgb_u8)
    write_rgb24(out_image, output_path)

    return { # Precisa de update
        "ok": True,
        "outputUrl": f"/outputs/{output_filename}",
        "logs": [
            f"config={cfg.config_name}",
            f"mask={cfg.mask_name}",
            f"mask_shape=({cfg.m}, {cfg.n})",
            f"stride={cfg.stride}",
            f"r={cfg.r}",
            f"activation={cfg.activation}",
            f"filter_type={cfg.filter_type}",
            f"input_shape={tuple(rgb_image.data.shape)}",
            f"output_shape={tuple(output_rgb_u8.shape)}",
            f"output_file={output_filename}",
            f"sobel_postprocess={'sim' if cfg.filter_type == 'sobel' else 'nao'}",
            "Pipeline executado com sucesso.",
        ],
    }