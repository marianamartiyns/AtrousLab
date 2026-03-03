from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import shutil
import json
import uuid

from app.settings import UPLOAD_DIR
from app.runner import run_pipeline

router = APIRouter()

@router.post("/run")
async def run_filter(
    config: UploadFile = File(...),
    image: UploadFile = File(...)
):
    try:
        run_id = str(uuid.uuid4())

        # Salvar config
        config_path = UPLOAD_DIR / f"{run_id}_config.json"
        with config_path.open("wb") as buffer:
            shutil.copyfileobj(config.file, buffer)

        # Salvar imagem
        image_path = UPLOAD_DIR / f"{run_id}_{image.filename}"
        with image_path.open("wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        # Executar pipeline
        result = run_pipeline(config_path, image_path, run_id)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))