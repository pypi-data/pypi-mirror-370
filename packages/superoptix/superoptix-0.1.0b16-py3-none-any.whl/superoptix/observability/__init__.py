"""SuperOptiX Observability and Monitoring Module."""

from .callbacks import SuperOptixCallback
from .debugger import InteractiveDebugger
from .tracer import SuperOptixTracer, TraceEvent

# Optional imports that require additional dependencies
try:
    from .dashboard import MultiAgentObservabilityDashboard, ObservabilityDashboard
except ImportError:
    ObservabilityDashboard = None
    MultiAgentObservabilityDashboard = None

from .enhanced_adapter import ObservabilityEnhancedDSPyAdapter

__all__ = [
    "SuperOptixTracer",
    "TraceEvent",
    "SuperOptixCallback",
    "InteractiveDebugger",
    "ObservabilityEnhancedDSPyAdapter",
]

# Add to __all__ only if successfully imported
if ObservabilityDashboard is not None:
    __all__.append("ObservabilityDashboard")

if MultiAgentObservabilityDashboard is not None:
    __all__.append("MultiAgentObservabilityDashboard")
