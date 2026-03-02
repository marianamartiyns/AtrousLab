from __future__ import annotations

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pathlib import Path
import shutil

from app.settings import UPLOAD_DIR
from app.runner import run_job

router = APIRouter(prefix="/api")


def _save_upload(file: UploadFile, dest: Path) -> None:
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)


@router.post("/run")
async def run_filter(
    config: UploadFile = File(...),
    image: UploadFile = File(...),
    makeSobelVis: str = Form("false"),
):
    # validações simples (ext)
    config_ext = Path(config.filename or "").suffix.lower()
    image_ext = Path(image.filename or "").suffix.lower()

    if config_ext != ".json":
        raise HTTPException(status_code=400, detail="Config deve ser .json")

    if image_ext not in {".png", ".tif", ".tiff"}:
        raise HTTPException(status_code=400, detail="Imagem deve ser .png, .tif ou .tiff")

    make_sobel_vis = makeSobelVis.strip().lower() == "true"

    # salva uploads
    config_path = UPLOAD_DIR / f"cfg_{config.filename}"
    image_path = UPLOAD_DIR / f"img_{image.filename}"

    try:
        _save_upload(config, config_path)
        _save_upload(image, image_path)

        result = run_job(config_path, image_path, make_sobel_vis)

        # devolve URL pública para o frontend baixar/ver
        out_url = f"/outputs/{result['outputFile']}"
        sobel_url = f"/outputs/{result['sobelVisFile']}" if result["sobelVisFile"] else None

        return {
            "ok": True,
            "outputUrl": out_url,
            "sobelVisUrl": sobel_url,
            "logs": result["logs"],
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))