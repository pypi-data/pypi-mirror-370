"""
Type definitions for NADFUN SDK.
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class BuyParams:
    """Parameters for buy transaction."""
    token: str
    amount_in: int
    amount_out_min: int
    to: Optional[str] = None
    deadline: Optional[int] = None

@dataclass
class SellParams:
    """Parameters for sell transaction."""
    token: str
    amount_in: int
    amount_out_min: int
    to: Optional[str] = None
    deadline: Optional[int] = None

@dataclass
class QuoteResult:
    """Result from quote functions."""
    router: str
    amount: int

@dataclass
class CurveData:
    """Bonding curve data."""
    reserve_mon: int
    reserve_token: int
    k: int
    token_supply: int
    virtual_mon: int
    virtual_token: int
    fee: int
    listed: bool

@dataclass
class TokenMetadata:
    """Token metadata information."""
    name: str
    symbol: str
    decimals: int
    total_supply: int
    address: str
