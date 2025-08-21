"""
NADFUN Python SDK
"""

from .trade import Trade
from .token import Token
from .types import BuyParams, SellParams, QuoteResult, CurveData, TokenMetadata
from .utils import calculate_slippage, parseMon
from .constants import CONTRACTS, CHAIN_ID, DEFAULT_DEADLINE_SECONDS, NADS_FEE_TIER

# Stream exports
from .stream import (
    CurveStream,
    DexStream,
    EventType,
    CurveEvent,
    DexSwapEvent
)

# Indexer exports
from .stream.curve.indexer import CurveIndexer
from .stream.dex.indexer import DexIndexer

__version__ = "0.1.2"

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
    
    # Indexers
    "CurveIndexer",
    "DexIndexer",
    
    # Utils
    "calculate_slippage",
    "parseMon",
    
    # Constants
    "CONTRACTS",
    "CHAIN_ID",
    "DEFAULT_DEADLINE_SECONDS",
    "NADS_FEE_TIER",
    
    "__version__",
]
