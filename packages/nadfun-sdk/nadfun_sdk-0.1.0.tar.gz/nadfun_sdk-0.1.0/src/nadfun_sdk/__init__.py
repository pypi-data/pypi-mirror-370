"""
NADFUN Python SDK
"""

from .trade import Trade
from .token import Token
from .types import BuyParams, SellParams, QuoteResult, CurveData, TokenMetadata
from .utils import calculate_slippage
from .constants import CONTRACTS, CHAIN_ID, DEFAULT_DEADLINE_SECONDS, NADS_FEE_TIER

# Stream exports
from .stream import (
    CurveStream,
    DexStream,
    EventType,
    CurveEvent,
    DexSwapEvent
)

__version__ = "0.1.0"

__all__ = [
    # Core classes
    "Trade",
    "Token",
    
    # Types
    "BuyParams",
    "SellParams",
    "QuoteResult",
    "CurveData",
    "TokenMetadata",
    
    # Stream
    "CurveStream",
    "DexStream",
    "EventType",
    "CurveEvent",
    "DexSwapEvent",
    
    # Utils
    "calculate_slippage",
    
    # Constants
    "CONTRACTS",
    "CHAIN_ID",
    "DEFAULT_DEADLINE_SECONDS",
    "NADS_FEE_TIER",
    
    "__version__",
]
