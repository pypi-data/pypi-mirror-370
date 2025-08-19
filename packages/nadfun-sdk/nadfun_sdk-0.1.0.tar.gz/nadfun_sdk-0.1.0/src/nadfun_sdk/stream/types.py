"""
Event types and data structures for streaming
"""

from enum import Enum
from typing import TypedDict, Optional, Union


class EventType(Enum):
    """Event types for streaming"""
    # Bonding Curve events
    BUY = "CurveBuy(address,address,uint256,uint256)"
    SELL = "CurveSell(address,address,uint256,uint256)"


class CurveEvent(TypedDict):
    """Bonding Curve event structure"""
    eventName: str          # "BUY" or "SELL"
    blockNumber: int        # Block number
    transactionHash: str    # Transaction hash
    trader: str            # Buyer/Seller address
    token: str             # Token address
    amountIn: int          # Amount in (MON for buy, tokens for sell)
    amountOut: int         # Amount out (tokens for buy, MON for sell)


class DexSwapEvent(TypedDict):
    """DEX Swap event structure"""
    eventName: str          # "Swap"
    blockNumber: int        # Block number
    transactionHash: str    # Transaction hash
    pool: str              # Pool address
    sender: str            # Sender address
    recipient: str         # Recipient address
    amount0: int           # Token0 amount (can be negative)
    amount1: int           # Token1 amount (can be negative)
    sqrtPriceX96: int      # Square root price
    liquidity: int         # Liquidity
    tick: int              # Price tick


# For backwards compatibility
from dataclasses import dataclass

@dataclass
class BaseEvent:
    """Base event structure"""
    block_number: int
    transaction_hash: str
    transaction_index: int
    log_index: int
    address: str
    timestamp: Optional[int] = None


@dataclass
class BuyEvent(BaseEvent):
    """Bonding Curve Buy event"""
    type: str = "Buy"
    token: str = ""
    buyer: str = ""
    amount_in: int = 0
    amount_out: int = 0
    reserve_mon: int = 0
    reserve_token: int = 0


@dataclass
class SellEvent(BaseEvent):
    """Bonding Curve Sell event"""
    type: str = "Sell"
    token: str = ""
    seller: str = ""
    amount_in: int = 0
    amount_out: int = 0
    reserve_mon: int = 0
    reserve_token: int = 0


@dataclass
class SwapEvent(BaseEvent):
    """Uniswap V3 Swap event"""
    type: str = "Swap"
    pool: str = ""
    sender: str = ""
    recipient: str = ""
    amount0: int = 0  # Can be negative
    amount1: int = 0  # Can be negative
    sqrt_price_x96: int = 0
    liquidity: int = 0
    tick: int = 0