# app/io/image_io.py
from __future__ import annotations

from pathlib import Path
from PIL import Image, UnidentifiedImageError
import numpy as np

from .models import RGBImage


class ImageIOError(Exception):
    pass

class ImageReadError(ImageIOError):
    pass

class ImageWriteError(ImageIOError):
    pass

class ImageShapeError(ImageIOError):
    pass


SUPPORTED_READ_EXTS = {".png", ".tif", ".tiff"}
SUPPORTED_WRITE_EXTS = {".png", ".tif", ".tiff"}


def read_rgb24(path: str | Path) -> RGBImage:
    p = Path(path)

    if not p.exists():
        raise ImageReadError(f"Imagem não encontrada: {p}")

    if p.suffix.lower() not in SUPPORTED_READ_EXTS:
        raise ImageReadError(f"Extensão não suportada: {p.suffix}. Use PNG/TIF/TIFF.")

    try:
        img = Image.open(p)
        img.load()
    except UnidentifiedImageError as e:
        raise ImageReadError(f"Arquivo não é uma imagem válida: {p}") from e
    except Exception as e:
        raise ImageReadError(f"Falha ao abrir imagem: {p}. Erro: {e}") from e

    try:
        rgb = img.convert("RGB")
    except Exception as e:
        raise ImageReadError(f"Falha ao converter para RGB: {p}. Erro: {e}") from e

    arr = np.asarray(rgb, dtype=np.uint8)

    if arr.ndim != 3 or arr.shape[2] != 3:
        raise ImageShapeError(f"Esperado H×W×3. Obtido: {arr.shape} em {p}")

    return RGBImage(path=str(p), data=arr)


def write_rgb24(image: RGBImage, out_path: str | Path) -> str:
    """
    Salva RGB (H,W,3) uint8 em PNG/TIF/TIFF.
    """
    p = Path(out_path)
    ext = p.suffix.lower()

    if ext not in SUPPORTED_WRITE_EXTS:
        raise ImageWriteError(f"Extensão de saída não suportada: {ext}. Use PNG/TIF/TIFF.")

    arr = image.data
    if arr.dtype != np.uint8 or arr.ndim != 3 or arr.shape[2] != 3:
        raise ImageShapeError(f"write_rgb24 esperava uint8 H×W×3. Recebido: dtype={arr.dtype}, shape={arr.shape}")

    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        img = Image.fromarray(arr, mode="RGB")
        img.save(p)
    except Exception as e:
        raise ImageWriteError(f"Falha ao salvar imagem em {p}: {e}") from e

    return str(p)