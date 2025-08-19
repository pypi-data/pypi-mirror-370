"""
Uniswap V3 DEX event stream with async iterator pattern
"""

import asyncio
import json
from typing import List, AsyncIterator, Optional, Dict, Any
from pathlib import Path
from web3 import AsyncWeb3, WebSocketProvider, Web3
from eth_abi import decode

from ...constants import CONTRACTS, NADS_FEE_TIER


class DexStream:
    def __init__(self, ws_url: str, debug: bool = False):
        self.ws_url = ws_url
        self.debug = debug
        self.token_addresses: List[str] = []
        self.pool_addresses: List[str] = []
        self._subscription_id: Optional[str] = None
        self._w3: Optional[AsyncWeb3] = None
        
    def subscribe_tokens(self, token_addresses):
        """Set which tokens to monitor (will find pools automatically)"""
        # Handle both single string and list of strings
        if isinstance(token_addresses, str):
            token_addresses = [token_addresses]
        self.token_addresses = [Web3.to_checksum_address(addr) for addr in token_addresses]
        
    async def _discover_pools(self, w3: AsyncWeb3) -> List[str]:
        """Discover V3 pools for configured tokens"""
        if not self.token_addresses:
            return []
            
        # Load factory ABI
        sdk_root = Path(__file__).parent.parent.parent
        abi_path = sdk_root / "abis" / "v3factory.json"
        
        with open(abi_path) as f:
            factory_abi = json.load(f)
        
        factory = w3.eth.contract(
            address=Web3.to_checksum_address(CONTRACTS["v3_factory"]),
            abi=factory_abi
        )
        
        wmon = Web3.to_checksum_address(CONTRACTS["wmon"])
        pools = []
        
        for token in self.token_addresses:
            if token.lower() == wmon.lower():
                continue
            
            try:
                # Sort tokens for pool address calculation
                token0, token1 = (token, wmon) if token.lower() < wmon.lower() else (wmon, token)
                
                # Get pool address for 1% fee tier
                pool_address = await factory.functions.getPool(
                    token0,
                    token1,
                    NADS_FEE_TIER
                ).call()
                
                if pool_address and pool_address != "0x0000000000000000000000000000000000000000":
                    pools.append(pool_address)
                    if self.debug:
                        print(f"Found pool for {token[:8]}...: {pool_address}")
            except Exception as e:
                if self.debug:
                    print(f"No pool found for {token[:8]}...")
        
        return pools
    
    async def events(self) -> AsyncIterator[Dict[str, Any]]:
        """Async iterator that yields parsed swap events"""
        # Connect
        async with AsyncWeb3(WebSocketProvider(self.ws_url)) as w3:
            self._w3 = w3
            
            # Discover pools
            self.pool_addresses = await self._discover_pools(w3)
            
            if not self.pool_addresses:
                if self.debug:
                    print("No pools found")
                return
            
            # Swap event signature
            swap_topic = Web3.keccak(text="Swap(address,address,int256,int256,uint160,uint128,int24)")
            
            # Create filter
            filter_params = {
                "address": self.pool_addresses,  # Multiple pool addresses
                "topics": [[swap_topic]]  # Just swap events
            }
            
            # Subscribe
            self._subscription_id = await w3.eth.subscribe("logs", filter_params)
            
            if self.debug:
                print(f"Subscribed: {self._subscription_id}")
            
            # Process events
            async for payload in w3.socket.process_subscriptions():
                if payload.get("subscription") != self._subscription_id:
                    continue
                    
                log = payload.get("result")
                if not log:
                    continue
                
                # Parse and yield event
                event = self._parse_swap_event(log)
                if event:
                    yield event
    
    def _parse_swap_event(self, log: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse swap event from log"""
        try:
            topics = log.get("topics", [])
            if len(topics) < 3:
                return None
            
            # Parse addresses from topics
            sender_topic = topics[1]
            recipient_topic = topics[2]
            
            # Handle HexBytes
            if hasattr(sender_topic, 'hex'):
                sender_hex = sender_topic.hex()
            else:
                sender_hex = sender_topic
            
            if hasattr(recipient_topic, 'hex'):
                recipient_hex = recipient_topic.hex()
            else:
                recipient_hex = recipient_topic
            
            # Extract addresses
            sender = Web3.to_checksum_address("0x" + sender_hex.replace('0x', '')[-40:])
            recipient = Web3.to_checksum_address("0x" + recipient_hex.replace('0x', '')[-40:])
            
            # Parse data
            data = log.get("data")
            if hasattr(data, 'hex'):
                data_bytes = data
            elif isinstance(data, str):
                data_bytes = bytes.fromhex(data.replace('0x', ''))
            else:
                data_bytes = data
            
            # Decode: [amount0, amount1, sqrtPriceX96, liquidity, tick]
            amount0, amount1, sqrt_price_x96, liquidity, tick = decode(
                ["int256", "int256", "uint160", "uint128", "int24"],
                data_bytes
            )
            
            # Handle transaction hash
            tx_hash = log.get("transactionHash")
            if hasattr(tx_hash, 'hex'):
                tx_hash = tx_hash.hex()
            
            return {
                "eventName": "Swap",
                "blockNumber": log.get("blockNumber"),
                "transactionHash": tx_hash,
                "pool": log.get("address"),
                "sender": sender,
                "recipient": recipient,
                "amount0": amount0,
                "amount1": amount1,
                "sqrtPriceX96": sqrt_price_x96,
                "liquidity": liquidity,
                "tick": tick,
            }
            
        except Exception as e:
            if self.debug:
                print(f"Parse error: {e}")
            return None