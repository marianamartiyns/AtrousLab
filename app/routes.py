from __future__ import annotations
from pathlib import Path
import shutil
import uuid
from fastapi import APIRouter, File, HTTPException, UploadFile
from app.runner import run_pipeline
from app.settings import UPLOAD_DIR

router = APIRouter()

CONFIG_EXTS = {".json"}
MASK_EXTS = {".txt"}
IMAGE_EXTS = {".png", ".tif", ".tiff"}


def _suffix_of(filename: str | None) -> str:
    if not filename:
        return ""
    return Path(filename).suffix.lower()


@router.post("/run")
async def run_filter(
    config: UploadFile = File(...),
    mask: UploadFile = File(...),
    image: UploadFile = File(...),
):
    try:
        config_ext = _suffix_of(config.filename)
        mask_ext = _suffix_of(mask.filename)
        image_ext = _suffix_of(image.filename)

        if config_ext not in CONFIG_EXTS:
            raise HTTPException(
                status_code=400,
                detail="Arquivo de configuração deve ser .json",
            )

        if mask_ext not in MASK_EXTS:
            raise HTTPException(
                status_code=400,
                detail="Arquivo de máscara deve ser .txt",
            )

        if image_ext not in IMAGE_EXTS:
            raise HTTPException(
                status_code=400,
                detail="Imagem deve ser .png, .tif ou .tiff",
            )

        run_id = str(uuid.uuid4())

        config_path = UPLOAD_DIR / f"{run_id}_config{config_ext}"
        mask_path = UPLOAD_DIR / f"{run_id}_mask{mask_ext}"
        image_name = Path(image.filename or "image.png").name
        image_path = UPLOAD_DIR / f"{run_id}_{image_name}"

        with config_path.open("wb") as buffer:
            shutil.copyfileobj(config.file, buffer)

        with mask_path.open("wb") as buffer:
            shutil.copyfileobj(mask.file, buffer)

        with image_path.open("wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        result = run_pipeline(
            config_path=config_path,
            mask_path=mask_path,
            image_path=image_path,
            run_id=run_id,
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")
    finally:
        try:
            await config.close()
        except Exception:
            pass
        try:
            await mask.close()
        except Exception:
            pass
        try:
            await image.close()
        except Exception:
            pass