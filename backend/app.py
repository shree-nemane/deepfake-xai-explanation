from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import analysis
from backend.persistence.database import init_db

app = FastAPI(title="Deepfake Forensic AI — Robustness Upgrade")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
