"""Temporal Gradient package.

Migration warning:
    Root-level modules in the repository (for example, ``chronos_engine.py`` and
    ``salience_pipeline.py``) are compatibility shims only. Prefer canonical
    package imports under ``temporal_gradient.*`` for all new usage.
"""

from . import clock, memory, policies, salience, telemetry
from .config_loader import load_config

__version__ = "0.2.0"

__all__ = ["clock", "memory", "policies", "salience", "telemetry", "load_config", "__version__"]
