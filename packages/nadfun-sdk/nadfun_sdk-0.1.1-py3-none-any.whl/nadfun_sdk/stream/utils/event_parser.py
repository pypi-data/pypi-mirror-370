"""
Event parsing utilities
"""

from typing import Optional, Any, Dict, List, Union
from web3 import Web3
from eth_abi import decode
from dataclasses import dataclass

from ..types import EventType, BuyEvent, SellEvent, BaseEvent


# Bonding Curve Event ABIs (event signatures for parsing)
# Based on actual ABI from curve.json
CURVE_EVENT_ABIS = {
    EventType.CREATE: "CurveCreate(address,address,address)",  # creator(indexed), token(indexed), pool(indexed) - all indexed, data in log
    EventType.BUY: "CurveBuy(address,address,uint256,uint256)",  # sender(indexed), token(indexed), amountIn, amountOut
    EventType.SELL: "CurveSell(address,address,uint256,uint256)",  # sender(indexed), token(indexed), amountIn, amountOut
    EventType.SYNC: "CurveSync(address,uint256,uint256,uint256,uint256)",  # token(indexed), realMonReserve, realTokenReserve, virtualMonReserve, virtualTokenReserve
    EventType.LOCK: "CurveTokenLocked(address)",  # token(indexed) only
    EventType.LISTED: "CurveTokenListed(address,address)",  # token(indexed), pool(indexed)
}

# DEX Event ABIs
SWAP_EVENT_ABI = "Swap(address,address,int256,int256,uint160,uint128,int24)"


@dataclass
class CreateEvent(BaseEvent):
    """Bonding Curve Create event"""
    type: str = "Create"
    token: str = ""
    creator: str = ""
    initial_supply: int = 0
    reserve_mon: int = 0
    reserve_token: int = 0


@dataclass
class SyncEvent(BaseEvent):
    """Bonding Curve Sync event"""
    type: str = "Sync"
    token: str = ""
    reserve_mon: int = 0
    reserve_token: int = 0


@dataclass
class LockEvent(BaseEvent):
    """Bonding Curve Lock event"""
    type: str = "Lock"
    token: str = ""
    locker: str = ""
    amount: int = 0


@dataclass
class ListedEvent(BaseEvent):
    """Bonding Curve Listed event"""
    type: str = "Listed"
    token: str = ""
    pool: str = ""


def _get_data_bytes(data) -> bytes:
    """Convert data from various formats to bytes"""
    if not data:
        return b""
    
    # Handle HexBytes
    if hasattr(data, 'hex'):
        return data
    
    # Handle string
    if isinstance(data, str):
        return bytes.fromhex(data[2:] if data.startswith('0x') else data)
    
    # Already bytes
    if isinstance(data, bytes):
        return data
    
    return b""


def get_event_signatures(event_types: List[EventType]) -> List[str]:
    """Get event signatures (topic0) for specified event types"""
    signatures = []
    for event_type in event_types:
        if event_type in CURVE_EVENT_ABIS:
            # Calculate keccak256 hash of event signature
            sig = CURVE_EVENT_ABIS[event_type]
            topic0 = "0x" + Web3.keccak(text=sig).hex()  # Add 0x prefix
            signatures.append(topic0)
    return signatures


def parse_bonding_curve_event(
    log: Dict[str, Any], 
    timestamp: Optional[int] = None
) -> Optional[BaseEvent]:
    """Parse a bonding curve event from a log"""
    
    # Get event signature from topic0
    topics = log.get("topics", [])
    if not topics:
        return None
    
    topic0 = topics[0]
    if isinstance(topic0, bytes):
        topic0 = topic0.hex()
    
    # Calculate expected event signatures
    event_map = {
        Web3.keccak(text=sig).hex(): event_type 
        for event_type, sig in CURVE_EVENT_ABIS.items()
    }
    
    if topic0 not in event_map:
        return None
    
    event_type = event_map[topic0]
    
    # Convert hex values to int if needed
    block_number = log.get("blockNumber")
    if isinstance(block_number, str):
        block_number = int(block_number, 16)
    
    tx_index = log.get("transactionIndex")
    if isinstance(tx_index, str):
        tx_index = int(tx_index, 16)
    
    log_index = log.get("logIndex")
    if isinstance(log_index, str):
        log_index = int(log_index, 16)
    
    base_event_data = {
        "block_number": block_number,
        "transaction_hash": log.get("transactionHash"),
        "transaction_index": tx_index,
        "log_index": log_index,
        "address": log.get("address"),
        "timestamp": timestamp,
    }
    
    # Parse specific event types
    if event_type == EventType.CREATE:
        # Topics: [signature, creator(indexed), token(indexed), pool(indexed)]
        # Data contains additional parameters
        data_bytes = _get_data_bytes(log.get("data"))
        
        # Handle HexBytes in topics
        topic1 = topics[1]  # creator
        topic2 = topics[2]  # token
        topic3 = topics[3]  # pool
        if hasattr(topic1, 'hex'):
            topic1 = topic1.hex()
        if hasattr(topic2, 'hex'):
            topic2 = topic2.hex()
        if hasattr(topic3, 'hex'):
            topic3 = topic3.hex()
        
        # Remove 0x prefix if present, then take last 40 chars (20 bytes)
        creator_addr = topic1[-40:] if topic1.startswith('0x') else topic1[26:]
        token_addr = topic2[-40:] if topic2.startswith('0x') else topic2[26:]
        
        # Decode data if present
        # The data may contain name, symbol, and other params
        # For now, we'll just extract addresses from topics
        return CreateEvent(
            **base_event_data,
            creator=Web3.to_checksum_address("0x" + creator_addr),
            token=Web3.to_checksum_address("0x" + token_addr),
            initial_supply=0,  # Not available directly from event
            reserve_mon=0,  # Not available directly from event
            reserve_token=0  # Not available directly from event
        )
    
    elif event_type == EventType.BUY:
        # Topics: [signature, sender(indexed), token(indexed)]
        # Data: [amountIn, amountOut]
        data = log.get("data")
        if data:
            # Handle both HexBytes and string
            if hasattr(data, 'hex'):
                data_bytes = data  # Already bytes
            else:
                # String format, remove 0x prefix and decode
                data_bytes = bytes.fromhex(data[2:] if data.startswith('0x') else data)
        else:
            data_bytes = b""
        
        decoded = decode(["uint256", "uint256"], data_bytes)
        
        # Handle HexBytes in topics
        topic1 = topics[1]
        topic2 = topics[2]
        if hasattr(topic1, 'hex'):
            topic1 = topic1.hex()
        if hasattr(topic2, 'hex'):
            topic2 = topic2.hex()
        
        # Remove 0x prefix if present, then take last 40 chars (20 bytes)
        buyer_addr = topic1[-40:] if topic1.startswith('0x') else topic1[26:]
        token_addr = topic2[-40:] if topic2.startswith('0x') else topic2[26:]
        
        return BuyEvent(
            **base_event_data,
            buyer=Web3.to_checksum_address("0x" + buyer_addr),  # sender is buyer
            token=Web3.to_checksum_address("0x" + token_addr),
            amount_in=decoded[0],
            amount_out=decoded[1],
            reserve_mon=0,  # Not provided in this event
            reserve_token=0  # Not provided in this event
        )
    
    elif event_type == EventType.SELL:
        # Topics: [signature, sender(indexed), token(indexed)]
        # Data: [amountIn, amountOut]
        data = log.get("data")
        if data:
            # Handle both HexBytes and string
            if hasattr(data, 'hex'):
                data_bytes = data  # Already bytes
            else:
                # String format, remove 0x prefix and decode
                data_bytes = bytes.fromhex(data[2:] if data.startswith('0x') else data)
        else:
            data_bytes = b""
        
        decoded = decode(["uint256", "uint256"], data_bytes)
        
        # Handle HexBytes in topics
        topic1 = topics[1]
        topic2 = topics[2]
        if hasattr(topic1, 'hex'):
            topic1 = topic1.hex()
        if hasattr(topic2, 'hex'):
            topic2 = topic2.hex()
        
        # Remove 0x prefix if present, then take last 40 chars (20 bytes)
        seller_addr = topic1[-40:] if topic1.startswith('0x') else topic1[26:]
        token_addr = topic2[-40:] if topic2.startswith('0x') else topic2[26:]
        
        return SellEvent(
            **base_event_data,
            seller=Web3.to_checksum_address("0x" + seller_addr),  # sender is seller
            token=Web3.to_checksum_address("0x" + token_addr),
            amount_in=decoded[0],
            amount_out=decoded[1],
            reserve_mon=0,  # Not provided in this event
            reserve_token=0  # Not provided in this event
        )
    
    elif event_type == EventType.SYNC:
        # Topics: [signature, token(indexed)]
        # Data: [realMonReserve, realTokenReserve, virtualMonReserve, virtualTokenReserve]
        data_bytes = _get_data_bytes(log.get("data"))
        decoded = decode(["uint256", "uint256", "uint256", "uint256"], data_bytes)
        
        # Handle HexBytes in topics
        topic1 = topics[1]
        if hasattr(topic1, 'hex'):
            topic1 = topic1.hex()
        
        # Remove 0x prefix if present, then take last 40 chars (20 bytes)
        token_addr = topic1[-40:] if topic1.startswith('0x') else topic1[26:]
        
        return SyncEvent(
            **base_event_data,
            token=Web3.to_checksum_address("0x" + token_addr),
            reserve_mon=decoded[0],  # realMonReserve
            reserve_token=decoded[1]  # realTokenReserve
        )
    
    elif event_type == EventType.LOCK:
        # Topics: [signature, token(indexed)]
        # Data: No data field for CurveTokenLocked
        # Handle HexBytes in topics
        topic1 = topics[1]
        if hasattr(topic1, 'hex'):
            topic1 = topic1.hex()
        
        # Remove 0x prefix if present, then take last 40 chars (20 bytes)
        token_addr = topic1[-40:] if topic1.startswith('0x') else topic1[26:]
        
        return LockEvent(
            **base_event_data,
            token=Web3.to_checksum_address("0x" + token_addr),
            locker="",  # No locker in this event
            amount=0  # No amount in this event
        )
    
    elif event_type == EventType.LISTED:
        # Topics: [signature, token(indexed), pool(indexed)]
        # Data: []
        # Handle HexBytes in topics
        topic1 = topics[1]
        topic2 = topics[2]
        if hasattr(topic1, 'hex'):
            topic1 = topic1.hex()
        if hasattr(topic2, 'hex'):
            topic2 = topic2.hex()
        
        # Remove 0x prefix if present, then take last 40 chars (20 bytes)
        token_addr = topic1[-40:] if topic1.startswith('0x') else topic1[26:]
        pool_addr = topic2[-40:] if topic2.startswith('0x') else topic2[26:]
        
        return ListedEvent(
            **base_event_data,
            token=Web3.to_checksum_address("0x" + token_addr),
            pool=Web3.to_checksum_address("0x" + pool_addr)
        )
    
    return None


def sort_events_chronologically(events: List[BaseEvent]) -> List[BaseEvent]:
    """Sort events chronologically"""
    return sorted(
        events,
        key=lambda e: (e.block_number, e.transaction_index, e.log_index)
    )