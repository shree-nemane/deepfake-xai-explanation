# Testing Patterns

**Analysis Date:** 2026-05-23

## Test Framework

**Runner:**
- `pytest` is the official automated test runner.

**Assertion Library:**
- Standard Python `assert` statements are evaluated inside the test suites.

**Run Commands:**
- Execute the complete test suite from the repository root:
  ```bash
  python -m pytest
  ```
- Run ESLint checks in the React frontend:
  ```bash
  cd frontend && npm run lint
  ```

## Test File Organization

All Python tests live under the dedicated `tests/` directory at the repository root:

```text
tests/
|-- conftest.py              # Shared pytest audio fixtures
|-- test_feature_analysis.py # Robustness checks for all agents
|-- test_pipeline.py         # End-to-end multi-agent pipeline tests
|-- test_reliability.py      # Consensus math and fail-closed checks
`-- test_validation.py       # Legacy schema validation checks
```

## Shared Fixtures (`tests/conftest.py`)

The test suite utilizes mock audio files committed in `mock_dataset/audio/` to run integration checks:

- `real_audio_path` & `fake_audio_path`: Resolves absolute local path locations for `mock_dataset/audio/real.wav` and `mock_dataset/audio/fake.wav`.
- `real_audio_data` & `fake_audio_data`: Dynamically loads audio paths at 16 kHz and 48 kHz using `librosa.load` and returns aligned tuple pairs.

## Mocking Strategy

- **Heavyweight Models**: Heavyweight deep learning models are tested on small, real-world mock files via the Pytest runner, allowing the lazy preload cache of `ModelHub` to persist model weights in-memory across the suite execution.
- **Fast Assertions**: Pure signal-processing logic (such as HPSS, z-score anomaly scoring, and dynamic calibration math) is validated by instantiating core classes (like `ConsensusEngine`, `CalibrationEngine`, and `ReliabilityAgent`) directly in-memory, avoiding GPU/CPU model loading overhead.

## Test Types & Verification

1. **Robustness Assertions (`test_feature_analysis.py`)**:
   - Loops over all registered agents in `agent_registry`.
   - Passes real and fake 1-second chunks through `agent.analyze_chunk`.
   - Assures the returns match the standard contract (`verdict`, `confidence`, `uncertainty`, `evidence`) and handle fallback failures gracefully.
2. **End-to-End Orchestration (`test_pipeline.py`)**:
   - Executes the complete `ForensicOrchestrator().analyze_audio` dual-stream pipeline on mock audio.
   - Verifies the response contains `agent_results`, `chunk_consensus`, and `global_consensus` schemas.
3. **Consensus Arbitration (`test_reliability.py`)**:
   - Verifies dynamic calibration, uncalibrated fallback, and tied votes.
   - Tests empty-registry fail-closed guards using `pytest.raises(AnalysisUnavailableError)`.

---

*Testing analysis: 2026-05-23*
