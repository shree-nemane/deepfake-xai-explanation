"""Register all forensic agents with the global registry.

Importing this package performs agent registration through each module's
existing ``agent_registry.register(...)`` side effect.
"""

from backend.agents import acoustic_agent  # noqa: F401
from backend.agents import aasist_agent  # noqa: F401
from backend.agents import convnext_agent  # noqa: F401
from backend.agents import reliability_agent  # noqa: F401
from backend.agents import wavlm_agent  # noqa: F401

