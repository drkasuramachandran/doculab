from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.tools import router as tools_router

app = FastAPI(
    title="DocuLab",
    description="All-in-one document, PDF and image toolkit",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "name": "DocuLab",
        "status": "running",
        "message": "DocuLab API is working",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


app.include_router(tools_router)
