# Deepfake Audio Detection & XAI Explanation System

A comprehensive forensic tool designed to detect synthetic (deepfake) audio and provide transparent, evidence-based explanations using Explainable AI (XAI) techniques.

## 🚀 Overview

This project implements a dual-layered detection pipeline:
1.  **Neural Classification**: Uses a fine-tuned `ConvNext-Tiny` model to analyze spectrogram patterns.
2.  **Forensic Feature Analysis**: A rule-based engine that evaluates acoustic properties like pitch stability, MFCC variance, and spectral centroids to provide human-interpretable evidence.

## ✨ Key Features

-   **Deepfake Detection**: High-accuracy classification of audio files as "Real" or "Fake".
-   **Visual Explanations (Grad-CAM)**: Generates heatmaps showing exactly which parts of the audio spectrogram influenced the AI's decision.
-   **Forensic Evidence Report**: Detailed breakdown of acoustic anomalies (e.g., unnaturally stable pitch or over-smoothed timbre).
-   **Similarity Analysis**: Compares the uploaded sample against known "Real" and "Fake" reference patterns.
-   **Professional Forensic Reports**: Generates a complete JSON/Visual report with risk statements and decision justifications.

## 🛠️ Tech Stack

-   **Backend**: 
    -   [FastAPI](https://fastapi.tiangolo.com/) (API Framework)
    -   [PyTorch](https://pytorch.org/) (Model Inference)
    -   [Librosa](https://librosa.org/) (Audio Processing)
    -   [Hugging Face Transformers](https://huggingface.co/docs/transformers/index) (Pre-trained Models)
-   **Frontend**: 
    -   [React](https://reactjs.org/) (UI Framework)
    -   [Vite](https://vitejs.dev/) (Build Tool)

## 📂 Project Structure

```text
.
├── backend/                # FastAPI source code
│   ├── app.py              # Main API entry point
│   ├── deepfake_logic.py   # Detection & XAI pipeline logic
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend (Vite)
│   ├── src/                # Component & Logic files
│   ├── package.json        # Frontend dependencies
│   └── vite.config.js      # Vite configuration
├── uploads/                # Temporary directory for uploaded files (ignored by git)
└── .gitignore              # Git ignore configurations
```

## ⚙️ Setup Instructions

### Prerequisites
-   Python 3.9 or higher
-   Node.js (v16+) and npm

### 1. Backend Setup

1.  Navigate to the project root.
2.  Create a virtual environment:
    ```bash
    python -m venv venv
    ```
3.  Activate the virtual environment:
    -   **Windows**: `venv\Scripts\activate`
    -   **macOS/Linux**: `source venv/bin/activate`
4.  Install dependencies:
    ```bash
    pip install -r backend/requirements.txt
    ```
5.  Run the backend server:
    ```bash
    python -m backend.app
    ```
    *The API will be available at `http://localhost:8000`.*

### 2. Frontend Setup

1.  Navigate to the `frontend` directory:
    ```bash
    cd frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Run the development server:
    ```bash
    npm run dev
    ```
    *The UI will be available at `http://localhost:5173`.*

## 📖 Usage

1.  Start both the backend and frontend servers.
2.  Open your browser to the frontend URL.
3.  Upload a `.wav` or `.mp3` audio file.
4.  Wait for the analysis to complete to view the forensic report, Grad-CAM heatmap, and feature breakdown.

## ⚖️ License

This project is intended for research and educational purposes.
