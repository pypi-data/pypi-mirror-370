"""
Historical event indexer for DEX swap events
"""

from typing import List, Dict, Any, Optional, Union
from web3 import AsyncWeb3, AsyncHTTPProvider
from eth_abi import decode

from ...constants import CONTRACTS, NADS_FEE_TIER
from ...stream.types import EventType
from ...utils import load_default_abis


class DexIndexer:
        
    def __init__(self, rpc_url: str):
        self.w3 = AsyncWeb3(AsyncHTTPProvider(rpc_url))
        self.factory_address = CONTRACTS["v3_factory"]
        self.wmon_address = CONTRACTS["wmon"]
        
        # Load factory ABI
        abis = load_default_abis()
        self.factory = self.w3.eth.contract(
            address=self.w3.to_checksum_address(self.factory_address),
            abi=abis["v3factory"]
        )
        
        # Pre-calculate swap topic hash
        self.swap_topic = self.w3.keccak(text=EventType.SWAP.value)
    
    async def fetch_events(
        self,
        from_block: int,
        to_block: int,
        pools: Optional[Union[str, List[str]]] = None,
        tokens: Optional[Union[str, List[str]]] = None
    ) -> List[Dict[str, Any]]:
        """Fetch historical swap events
        
        Args:
            from_block: Starting block number
            to_block: Ending block number
            pools: Pool address(es) to filter (optional)
            tokens: Token address(es) to find pools for (optional)
            
        Returns:
            List of parsed swap events
        """
        # Handle pool filter
        pool_addresses = None
        
        # If tokens provided, find their pools
        if tokens:
            pool_addresses = await self.get_pools_for_tokens(tokens)
            if not pool_addresses:
                return []  # No pools found for these tokens
        elif pools:
            if isinstance(pools, str):
                pool_addresses = [self.w3.to_checksum_address(pools)]
            else:
                pool_addresses = [self.w3.to_checksum_address(p) for p in pools]
        
        # Build topics array
        topics = [self.swap_topic.hex()]
        
        # Scan in chunks to avoid API limits
        chunk_size = 1000
        all_events = []
        current_block = from_block
        
        while current_block <= to_block:
            chunk_end = min(current_block + chunk_size - 1, to_block)
            
            try:
                # Create filter parameters
                filter_params = {
                    "topics": topics,
                    "fromBlock": current_block,
                    "toBlock": chunk_end
                }
                
                # Add address filter if pools specified
                if pool_addresses:
                    filter_params["address"] = pool_addresses
                
                # Get logs
                logs = await self.w3.eth.get_logs(filter_params)
                
                # Parse events
                for log in logs:
                    event = await self._parse_swap_event(log)
                    if event:
                        all_events.append(event)
                
                current_block = chunk_end + 1
                
            except Exception as e:
                # Reduce chunk size on error
                if chunk_size > 100:
                    chunk_size = chunk_size // 2
                    continue
                else:
                    raise e
        
        return all_events
    
    async def get_pools_for_tokens(self, tokens: Union[str, List[str]]) -> List[str]:
        """Get all V3 pools for given token(s)
        
        Args:
            tokens: Token address(es) to find pools for
            
        Returns:
            List of pool addresses
        """
        if isinstance(tokens, str):
            tokens = [tokens]
        
        pools = []
        wmon = self.w3.to_checksum_address(self.wmon_address)
        
        # For each token, find pools with WMON
        for token in tokens:
            token = self.w3.to_checksum_address(token)
            
            # Skip if token is WMON itself
            if token.lower() == wmon.lower():
                continue
            
            # Get pool address (token0 < token1 ordering)
            if token.lower() < wmon.lower():
                token0, token1 = token, wmon
            else:
                token0, token1 = wmon, token
            
            # Query factory for pools with different fee tiers
            # Use NADS_FEE_TIER as the primary fee tier
            try:
                pool_address = await self.factory.functions.getPool(
                    token0,
                    token1,
                    NADS_FEE_TIER
                ).call()
                
                # Add pool if it exists (non-zero address)
                if pool_address != '0x0000000000000000000000000000000000000000':
                    pools.append(self.w3.to_checksum_address(pool_address))
                    
            except Exception as e:
                print(f"Error getting pool for {token}: {e}")
        
        return pools
    
    async def _parse_swap_event(self, log: Dict) -> Optional[Dict[str, Any]]:
        """Parse a swap log entry into an event"""
        try:
            # Parse indexed parameters (topics)
            # topics[1] = sender, topics[2] = recipient
            sender_bytes = bytes.fromhex(
                log['topics'][1].hex()[2:] if hasattr(log['topics'][1], 'hex') 
                else log['topics'][1][2:]
            )
            recipient_bytes = bytes.fromhex(
                log['topics'][2].hex()[2:] if hasattr(log['topics'][2], 'hex')
                else log['topics'][2][2:]
            )
            
            sender = "0x" + sender_bytes[-20:].hex()
            recipient = "0x" + recipient_bytes[-20:].hex()
            
            # Parse non-indexed parameters (data)
            data = log['data']
            if isinstance(data, str):
                data_bytes = bytes.fromhex(data[2:])
            else:
                data_bytes = data
            
            # Decode: int256 amount0, int256 amount1, uint160 sqrtPriceX96, uint128 liquidity, int24 tick
            amount0, amount1, sqrt_price, liquidity, tick = decode(
                ["int256", "int256", "uint160", "uint128", "int24"], 
                data_bytes
            )
            
            # Get block timestamp
            block = await self.w3.eth.get_block(log['blockNumber'])
            
            # Get pool address from log
            pool_address = log['address']
            if hasattr(pool_address, 'hex'):
                pool_address = pool_address.hex()
            elif not pool_address.startswith('0x'):
                pool_address = '0x' + pool_address
            
            return {
                "eventName": "Swap",
                "blockNumber": log['blockNumber'],
                "transactionHash": (
                    log['transactionHash'].hex() 
                    if hasattr(log['transactionHash'], 'hex') 
                    else log['transactionHash']
                ),
                "logIndex": log['logIndex'],
                "pool": self.w3.to_checksum_address(pool_address),
                "sender": self.w3.to_checksum_address(sender),
                "recipient": self.w3.to_checksum_address(recipient),
                "amount0": amount0,
                "amount1": amount1,
                "sqrtPriceX96": sqrt_price,
                "liquidity": liquidity,
                "tick": tick,
                "timestamp": block['timestamp'],
            }
            
        except Exception as e:
            print(f"Error parsing swap event: {e}")
            return None
    
    async def get_block_number(self) -> int:
        """Get current block number"""
        return await self.w3.eth.get_block_number()