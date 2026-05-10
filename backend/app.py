import os
import uuid
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.deepfake_logic import run_pipeline, GradCAM
from transformers import ConvNextForImageClassification
import torch

app = FastAPI(title="Deepfake Audio Detection API")

# 1. CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Globals (Loaded once on startup)
MODEL = None
GRADCAM_ENGINE = None
UPLOADS_DIR = "uploads"

if not os.path.exists(UPLOADS_DIR):
    os.makedirs(UPLOADS_DIR)

@app.on_event("startup")
async def startup_event():
    global MODEL, GRADCAM_ENGINE
    print("Loading Forensic Model...")
    model_name = "kubinooo/convnext-tiny-224-audio-deepfake-classification"
    MODEL = ConvNextForImageClassification.from_pretrained(model_name)
    MODEL.eval()
    
    # Init Grad-CAM
    target_layer = MODEL.convnext.encoder.stages[3].layers[-1].dwconv
    GRADCAM_ENGINE = GradCAM(MODEL, target_layer)
    print("Model loaded and Grad-CAM initialized.")

@app.get("/")
async def health_check():
    return {"status": "online", "message": "Deepfake Audio Detection API is running."}

@app.post("/analyze")
async def analyze_audio(file: UploadFile = File(...)):
    # 3. File Type Validation
    if not file.filename.lower().endswith(('.wav', '.mp3')):
        raise HTTPException(status_code=400, detail="Invalid file type. Only .wav and .mp3 are supported.")

    # 4. Unique Filename Generation
    file_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1]
    temp_path = os.path.join(UPLOADS_DIR, f"{file_id}{ext}")

    print(f"\n--- [REQUEST] Analyzing: {file.filename} (Internal ID: {file_id}) ---")

    try:
        # 5. Reset file pointer (Ensure fresh read)
        await file.seek(0)
        
        # 6. Save File Safely
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 7. Run Pipeline
        result, error = run_pipeline(temp_path, MODEL, GRADCAM_ENGINE)

        if error:
            print(f"--- [ERROR] Analysis failed for {file_id}: {error} ---")
            return {"status": "error", "message": error}

        prediction = result['report']['Prediction']
        confidence = result['report']['Confidence']['calibrated']
        print(f"--- [SUCCESS] {file_id} Result: {prediction} ({confidence:.2%}) ---")
        return {"status": "success", "data": result}

    except Exception as e:
        return {"status": "error", "message": f"Server error: {str(e)}"}

    finally:
        # 7. Guaranteed Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
