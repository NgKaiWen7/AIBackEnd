from fastapi import FastAPI

from aibackend.api.ingestion import router as ingestion_router
from aibackend.logging_config import setup_logging

setup_logging()


app = FastAPI(title="AI Backend", version="0.1.0")

app.include_router(ingestion_router)
