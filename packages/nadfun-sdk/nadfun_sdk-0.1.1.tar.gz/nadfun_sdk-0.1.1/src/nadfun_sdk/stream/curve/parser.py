"""
Curve event parser utilities
"""

from typing import Optional, Dict, Any
from web3 import Web3
from eth_abi import decode


def parse_curve_event(log: Dict[str, Any], event_name: str) -> Optional[Dict[str, Any]]:
    """
    Parse Curve event log
    
    Args:
        log: Web3 log dict
        event_name: "BUY" or "SELL"
    
    Returns:
        Parsed event dict or None
    """
    try:
        topics = log.get("topics", [])
        if len(topics) < 3:
            return None
        
        # Parse addresses from topics
        sender_topic = topics[1]
        token_topic = topics[2]
        
        # Handle HexBytes
        if hasattr(sender_topic, 'hex'):
            sender_hex = sender_topic.hex()
        else:
            sender_hex = sender_topic
        
        if hasattr(token_topic, 'hex'):
            token_hex = token_topic.hex()
        else:
            token_hex = token_topic
        
        # Extract addresses (last 40 chars)
        sender = Web3.to_checksum_address("0x" + sender_hex.replace('0x', '')[-40:])
        token = Web3.to_checksum_address("0x" + token_hex.replace('0x', '')[-40:])
        
        # Parse data
        data = log.get("data")
        if hasattr(data, 'hex'):
            data_bytes = data
        elif isinstance(data, str):
            data_bytes = bytes.fromhex(data.replace('0x', ''))
        else:
            data_bytes = data
        
        # Decode amounts
        amount_in, amount_out = decode(["uint256", "uint256"], data_bytes)
        
        # Handle transaction hash
        tx_hash = log.get("transactionHash")
        if hasattr(tx_hash, 'hex'):
            tx_hash = tx_hash.hex()
        
        return {
            "eventName": event_name,
            "blockNumber": log.get("blockNumber"),
            "transactionHash": tx_hash,
            "trader": sender,  # More descriptive name
            "token": token,
            "amountIn": amount_in,
            "amountOut": amount_out,
        }
        
    except Exception:
        return None