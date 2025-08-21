from nqs_sdk.nqs_sdk import (
    LPTokenUniv3,
    MetricName,
    Metrics,
    MutBuilderSharedState,
    MutSharedState,
    ObservableDescription,
    Parameters,
    ProtocolFactoryAdapter,
    RefSharedState,
    SealedParameters,
    SimulationClock,
    SimulationTime,
    Simulator,
    SimulatorBuilder,
    TokenMetadata,
    TxRequest,
    Wallet,
    implementations,
    quantlib,
)

from . import version
from .core.simulation import Simulation


BlockNumberOrTimestamp = quantlib.BlockNumberOrTimestamp

# Expose version at package level
__version__ = version.__version__

# Initialize logging subsystem for the NQS SDK
#
# It activates the logging system, enabling detailed tracking of
# simulation execution, transaction processing, and error reporting.
# It configures both Python and Rust logging components
#
# Logging activation failures don't prevent SDK functionality,
# they just reduce observability
try:
    from nqs_sdk.nqs_sdk import activate_log

    activate_log()
    del activate_log
except Exception:
    pass

__all__ = [
    "Simulation",
    "BlockNumberOrTimestamp",
    "LPTokenUniv3",
    "MetricName",
    "Metrics",
    "MutBuilderSharedState",
    "MutSharedState",
    "ObservableDescription",
    "Parameters",
    "ProtocolFactoryAdapter",
    "RefSharedState",
    "SealedParameters",
    "SimulationClock",
    "SimulationTime",
    "Simulator",
    "SimulatorBuilder",
    "TokenMetadata",
    "TxRequest",
    "Wallet",
    "implementations",
    "quantlib",
    "__version__",
]
