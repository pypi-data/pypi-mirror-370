"""Soda: A CLI tool for managing agentic DSL configurations."""

# ---------------------------------------------------------------------------
# Global warning filters
# ---------------------------------------------------------------------------
# Pydantic v2 raises a verbose UserWarning when serialising dynamic objects
# (e.g. DSPy Message / Choices) with a different field shape. These are
# harmless for SuperOptiX users and clutter the console, so we silence them
# once at package import time.  Down-stream modules (CLI runners, notebooks)
# inherit the filter automatically.

import warnings

# Match any variant of the warning header
warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    message=r"Pydantic serializer warnings.*",
)

__version__ = "0.1.0b16"
