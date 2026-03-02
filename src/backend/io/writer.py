from __future__ import annotations

from pathlib import Path
import numpy as np
from PIL import Image

from .errors import ImageWriteError, ImageShapeError

SUPPORTED_SAVE_EXTS = {".png", ".tif", ".tiff"}

def write_rgb24(path: str | Path, data: np.ndarray) -> None:
    """
    Salva matriz H×W×3 uint8 como PNG/TIF/TIFF (RGB 24 bits).
    """
    p = Path(path)

    if p.suffix.lower() not in SUPPORTED_SAVE_EXTS:
        raise ImageWriteError(f"Extensão para salvar não suportada: {p.suffix}")

    if not isinstance(data, np.ndarray):
        raise ImageShapeError("data deve ser um np.ndarray")

    if data.ndim != 3 or data.shape[2] != 3:
        raise ImageShapeError(f"Esperado H×W×3. Obtido: {data.shape}")

    if data.dtype != np.uint8:
        raise ImageWriteError(f"Esperado dtype uint8. Obtido: {data.dtype}")

    try:
        img = Image.fromarray(data, mode="RGB")
        img.save(p)
    except Exception as e:
        raise ImageWriteError(f"Falha ao salvar em {p}: {e}") from e