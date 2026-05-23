from fastapi.testclient import TestClient
from backend.app import app
import json
import traceback
import sys

client = TestClient(app)

samples = ["test_audio.wav", "fake-1.wav", "fake-2.wav"]

print("Sending audio samples to new integration endpoint...")
try:
    for sample in samples:
        print(f"Sending {sample}...")
        with open(sample, "rb") as f:
            response = client.post("/analyze/", files={"file": (sample, f, "audio/wav")})

        print(f"Status Code: {response.status_code}")
        if response.status_code != 200:
            print("Error:")
            print(response.json())
            sys.exit(1)

        data = response.json()
        agents = data.get("agents", {})
        timeline = data.get("timeline", [])
        consensus = data.get("consensus", {})

        if not agents:
            raise AssertionError("No agents returned in analysis response.")
        if not timeline:
            raise AssertionError("No timeline returned in analysis response.")
        if consensus.get("verdict") == "real" and not any(
            agent.get("verdict") == "real" for agent in agents.values()
        ):
            raise AssertionError("Consensus returned real without a real-voting agent.")

        print(f"Consensus Verdict: {consensus.get('verdict')}")
        print(f"Agents: {', '.join(agents.keys())}")
        print(f"Timeline events: {len(timeline)}")

    print("Integration successfully returned active agent evidence for all samples.")
except Exception as e:
    traceback.print_exc()
    sys.exit(1)
