"""
Shared Model Hub — Singleton that lazily loads all ML models once and shares
them across forensic agents, avoiding duplicate GPU memory allocations.

Usage:
    from backend.agents.model_hub import model_hub

    handler = model_hub.convnext_handler   # loaded on first access
    cam     = model_hub.gradcam_engine     # loaded on first access
"""

import logging
import threading
import torch

logger = logging.getLogger(__name__)


class ModelHub:
    """Thread-safe singleton that lazily loads heavyweight ML artefacts."""

    _instance = None
    _init_lock = threading.Lock()

    # ── Singleton ────────────────────────────────────────────────────────
    def __new__(cls):
        if cls._instance is None:
            with cls._init_lock:
                # Double-checked locking
                if cls._instance is None:
                    inst = super().__new__(cls)
                    inst._initialised = False
                    cls._instance = inst
        return cls._instance

    def __init__(self):
        if self._initialised:
            return
        with self._init_lock:
            if self._initialised:
                return
            self._convnext_handler = None
            self._wavlm_handler = None
            self._gradcam_engine = None
            self._uncertainty_engine = None
            self._device = None
            # Per-property locks so independent models can load in parallel
            self._convnext_lock = threading.Lock()
            self._wavlm_lock = threading.Lock()
            self._gradcam_lock = threading.Lock()
            self._uncertainty_lock = threading.Lock()
            self._initialised = True

    # ── Device ───────────────────────────────────────────────────────────
    @property
    def device(self) -> torch.device:
        """Resolve compute device (cached after first call)."""
        if self._device is None:
            self._device = torch.device(
                "cuda" if torch.cuda.is_available() else "cpu"
            )
            logger.info("ModelHub device resolved to %s", self._device)
        return self._device

    # ── ConvNext ─────────────────────────────────────────────────────────
    @property
    def convnext_handler(self):
        """Lazily load the ConvNext spectrogram classifier."""
        if self._convnext_handler is None:
            with self._convnext_lock:
                if self._convnext_handler is None:
                    logger.info("Loading ConvNextHandler …")
                    from backend.models.convnext.convnext_handler import (
                        ConvNextHandler,
                    )
                    self._convnext_handler = ConvNextHandler(self.device)
                    logger.info("ConvNextHandler ready on %s", self.device)
        return self._convnext_handler

    # WavLM
    @property
    def wavlm_handler(self):
        """Lazily load the WavLM embedding extractor."""
        if self._wavlm_handler is None:
            with self._wavlm_lock:
                if self._wavlm_handler is None:
                    logger.info("Loading WavLMHandler …")
                    from backend.models.wavlm.wavlm_handler import (
                        WavLMHandler,
                    )
                    self._wavlm_handler = WavLMHandler(self.device)
                    logger.info("WavLMHandler ready on %s", self.device)
        return self._wavlm_handler

    # ── Grad-CAM ─────────────────────────────────────────────────────────
    @property
    def gradcam_engine(self):
        """Lazily initialise Grad-CAM over the ConvNext backbone."""
        if self._gradcam_engine is None:
            with self._gradcam_lock:
                if self._gradcam_engine is None:
                    logger.info("Loading GradCAMEngine …")
                    from backend.explainability.gradcam.gradcam_engine import (
                        GradCAMEngine,
                    )
                    handler = self.convnext_handler  # ensures ConvNext is loaded
                    self._gradcam_engine = GradCAMEngine(
                        model=handler.model,
                        target_layer=handler.get_target_layer(),
                    )
                    logger.info("GradCAMEngine ready")
        return self._gradcam_engine

    # ── Uncertainty ──────────────────────────────────────────────────────
    @property
    def uncertainty_engine(self):
        """Lazily initialise MC-Dropout uncertainty estimator."""
        if self._uncertainty_engine is None:
            with self._uncertainty_lock:
                if self._uncertainty_engine is None:
                    logger.info("Loading UncertaintyEngine …")
                    from backend.forensic.confidence.uncertainty_engine import (
                        UncertaintyEngine,
                    )
                    handler = self.convnext_handler  # ensures ConvNext is loaded
                    self._uncertainty_engine = UncertaintyEngine(
                        model=handler.model,
                    )
                    logger.info("UncertaintyEngine ready")
        return self._uncertainty_engine

    # ── Utilities ────────────────────────────────────────────────────────
    def preload_all(self):
        """Eagerly load every model (useful at server start-up)."""
        _ = self.convnext_handler
        _ = self.wavlm_handler
        _ = self.gradcam_engine
        _ = self.uncertainty_engine
        logger.info("All ModelHub artefacts pre-loaded")

    def status(self) -> dict:
        """Return a quick summary of what is currently loaded."""
        return {
            "device": str(self.device),
            "convnext_loaded": self._convnext_handler is not None,
            "wavlm_loaded": self._wavlm_handler is not None,
            "gradcam_loaded": self._gradcam_engine is not None,
            "uncertainty_loaded": self._uncertainty_engine is not None,
        }


# ── Module-level singleton ───────────────────────────────────────────────
model_hub = ModelHub()
