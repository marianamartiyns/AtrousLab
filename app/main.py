from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import router
from app.settings import OUTPUT_DIR

app = FastAPI(
    title="Aplicação de Correlação Dilatada RGB",
    description=(
        "Sistema para processamento de imagens RGB 24 bits usando correlação dilatada."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.mount("/outputs", StaticFiles(directory=str(OUTPUT_DIR)), name="outputs")


@app.get("/")
def root():
    return {
        "ok": True,
        "message": "Backend da aplicação de correlação RGB está em execução."
    }