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
    """
    Lê uma imagem PNG/TIF/TIFF e converte explicitamente para RGB 24 bits.
    Retorna RGBImage com data no formato H x W x 3 uint8.
    """
    p = Path(path)

    if not p.exists():
        raise ImageReadError(f"Imagem não encontrada: {p}")

    if not p.is_file():
        raise ImageReadError(f"Caminho não é um arquivo: {p}")

    if p.suffix.lower() not in SUPPORTED_READ_EXTS:
        raise ImageReadError(
            f"Extensão não suportada: {p.suffix}. Use PNG, TIF ou TIFF."
        )

    try:
        with Image.open(p) as img:
            rgb = img.convert("RGB")
            arr = np.asarray(rgb, dtype=np.uint8)
    except UnidentifiedImageError as e:
        raise ImageReadError(f"Arquivo não é uma imagem válida: {p}") from e
    except Exception as e:
        raise ImageReadError(f"Falha ao abrir imagem {p}: {e}") from e

    if arr.ndim != 3 or arr.shape[2] != 3:
        raise ImageShapeError(f"Esperado H x W x 3. Obtido: {arr.shape} em {p}")

    if arr.dtype != np.uint8:
        raise ImageShapeError(
            f"Esperado uint8 após conversão RGB. Obtido: {arr.dtype} em {p}"
        )

    return RGBImage(path=str(p), data=arr)


def write_rgb24(image: RGBImage, out_path: str | Path) -> str:
    """
    Salva uma RGBImage no formato PNG/TIF/TIFF.
    Exige H x W x 3 uint8.
    """
    p = Path(out_path)
    ext = p.suffix.lower()

    if ext not in SUPPORTED_WRITE_EXTS:
        raise ImageWriteError(
            f"Extensão de saída não suportada: {ext}. Use PNG, TIF ou TIFF."
        )

    arr = image.data
    if not isinstance(arr, np.ndarray):
        raise ImageShapeError("image.data deve ser np.ndarray.")

    if arr.ndim != 3 or arr.shape[2] != 3:
        raise ImageShapeError(
            f"write_rgb24 esperava H x W x 3. Recebido: {arr.shape}"
        )

    if arr.dtype != np.uint8:
        raise ImageShapeError(
            f"write_rgb24 esperava uint8. Recebido: {arr.dtype}"
        )

    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        img = Image.fromarray(arr, mode="RGB")
        img.save(p)
    except Exception as e:
        raise ImageWriteError(f"Falha ao salvar imagem em {p}: {e}") from e

    return str(p)