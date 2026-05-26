"""Smoke-test the forensic API with local sample wav files (project root)."""

from pathlib import Path
import sys
import traceback

from fastapi.testclient import TestClient

from backend.app import app

ROOT = Path(__file__).resolve().parents[1]
client = TestClient(app)

samples = ["test_audio.wav", "fake-1.wav", "fake-2.wav"]
available = [name for name in samples if (ROOT / name).is_file()]

if not available:
    print("No sample wav files in project root; skipping analyze smoke test.")
    health = client.get("/")
    assert health.status_code == 200, health.text
    print("Health check OK:", health.json())
    sys.exit(0)

print("Sending audio samples to POST /analyze/ ...")
try:
    for sample in available:
        path = ROOT / sample
        print(f"  {sample} ...")
        with path.open("rb") as handle:
            response = client.post("/analyze/", files={"file": (sample, handle, "audio/wav")})

        if response.status_code != 200:
            print("Error:", response.status_code, response.text)
            sys.exit(1)

        data = response.json()
        agents = data.get("agents", {})
        timeline = data.get("timeline", [])
        consensus = data.get("consensus", {})
        diagnostics = data.get("diagnostics") or {}

        if not agents:
            raise AssertionError("No agents returned in analysis response.")
        if not timeline:
            raise AssertionError("No timeline returned in analysis response.")

        for warning in diagnostics.get("warnings") or []:
            if not isinstance(warning, (str, dict)):
                raise AssertionError(f"Unexpected warning type: {type(warning)}")

        print(
            f"    verdict={consensus.get('verdict')} "
            f"agents={len(agents)} timeline={len(timeline)}"
        )

    print("Smoke test passed.")
except Exception:
    traceback.print_exc()
    sys.exit(1)
