from __future__ import annotations

from pathlib import Path
from PIL import Image, UnidentifiedImageError
import numpy as np

from .errors import ImageReadError, ImageShapeError
from .models import RGBImage

SUPPORTED_EXTS = {".png", ".tif", ".tiff"}

def read_rgb24(path: str | Path) -> RGBImage:
    """
    Lê PNG/TIF e garante RGB 24 bits (8 bits por canal).
    Retorna RGBImage com matriz H×W×3 uint8.
    """
    p = Path(path)

    if not p.exists():
        raise ImageReadError(f"Imagem não encontrada: {p}")

    if p.suffix.lower() not in SUPPORTED_EXTS:
        raise ImageReadError(f"Extensão não suportada: {p.suffix}. Use PNG/TIF/TIFF.")

    try:
        img = Image.open(p)
        img.load()
    except UnidentifiedImageError as e:
        raise ImageReadError(f"Arquivo não é uma imagem válida: {p}") from e
    except Exception as e:
        raise ImageReadError(f"Falha ao abrir imagem: {p}. Erro: {e}") from e

    # Converte qualquer coisa para RGB 8-bit por canal
    try:
        rgb = img.convert("RGB")
    except Exception as e:
        raise ImageReadError(f"Falha ao converter para RGB: {p}. Erro: {e}") from e

    arr = np.asarray(rgb, dtype=np.uint8)

    if arr.ndim != 3 or arr.shape[2] != 3:
        raise ImageShapeError(f"Esperado H×W×3. Obtido: {arr.shape} em {p}")

    return RGBImage(path=str(p), data=arr)