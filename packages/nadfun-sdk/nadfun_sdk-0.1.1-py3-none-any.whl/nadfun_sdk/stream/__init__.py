"""
Stream module for real-time event monitoring
"""

from .curve import CurveStream
from .dex import DexStream
from .types import (
    EventType,
    CurveEvent,
    DexSwapEvent,
    # Legacy dataclass events
    BaseEvent,
    BuyEvent, 
    SellEvent, 
    SwapEvent
)

__all__ = [
    "CurveStream",
    "DexStream", 
    "EventType",
    "CurveEvent",
    "DexSwapEvent",
    # Legacy
    "BaseEvent",
    "BuyEvent",
    "SellEvent",
    "SwapEvent",
]