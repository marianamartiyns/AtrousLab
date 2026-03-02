from __future__ import annotations

from pathlib import Path
from typing import Dict, Any
import time

from app.settings import OUTPUT_DIR

from src.backend.config import load_config
from src.backend.io import read_rgb24, write_rgb24
from src.backend.pipeline import run_rgb_pipeline
from src.backend.post import sobel_visualize_rgb


def run_job(config_path: Path, image_path: Path, make_sobel_vis: bool) -> Dict[str, Any]:
    logs: list[str] = []
    t0 = time.time()

    logs.append(f"Config: {config_path.name}")
    logs.append(f"Imagem: {image_path.name}")

    cfg = load_config(config_path)
    logs.append(f"Params: stride={cfg.stride}, r={cfg.r}, activation={cfg.activation}")
    logs.append(f"Mask file: {cfg.mask_file} | mask={cfg.m}x{cfg.n}")

    img = read_rgb24(image_path)
    logs.append(f"Imagem carregada: {img.width}x{img.height}")

    result = run_rgb_pipeline(
        rgb_u8=img.data,
        mask=cfg.mask,
        r=cfg.r,
        stride=cfg.stride,
        activation=cfg.activation,
        make_visualization=False,  # visualização Sobel faremos no módulo 7
    )

    # Salva resultado “normal” (RGB clipado)
    out_name = f"result_{int(time.time()*1000)}.png"
    out_path = OUTPUT_DIR / out_name
    write_rgb24(out_path, result.out_rgb_u8)
    logs.append(f"Resultado salvo: {out_name}")

    sobel_name = None
    if make_sobel_vis:
        vis = sobel_visualize_rgb(result.out_r, result.out_g, result.out_b)
        sobel_name = f"sobelvis_{int(time.time()*1000)}.png"
        sobel_path = OUTPUT_DIR / sobel_name
        write_rgb24(sobel_path, vis)
        logs.append(f"Sobel vis salvo: {sobel_name}")

    logs.append(f"Tempo total: {time.time()-t0:.3f}s")

    return {
        "ok": True,
        "outputFile": out_name,
        "sobelVisFile": sobel_name,
        "logs": logs,
    }