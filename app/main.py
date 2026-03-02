from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routes import router
from app.settings import OUTPUT_DIR

app = FastAPI(title="Filtro RGB - Orquestrador")

# Em dev, libera CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # em produção, restrinja
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

# Servir arquivos gerados
app.mount("/outputs", StaticFiles(directory=str(OUTPUT_DIR)), name="outputs")