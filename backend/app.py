from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import analysis
from backend.persistence.database import init_db

app = FastAPI(title="Deepfake Forensic AI — Robustness Upgrade")

# CORS — explicit dev origins (wildcard + credentials is invalid in browsers)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Database
init_db()

# Include Routes
app.include_router(analysis.router)

@app.get("/")
async def root():
    return {"status": "online", "message": "Deepfake Forensic AI API is operational."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)
