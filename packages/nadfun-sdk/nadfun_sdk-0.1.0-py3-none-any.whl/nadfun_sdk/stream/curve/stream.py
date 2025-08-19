"""
Curve event stream with async iterator pattern
"""

import asyncio
from typing import List, AsyncIterator, Optional, Dict, Any
from web3 import AsyncWeb3, WebSocketProvider
from nadfun_sdk.stream.types import EventType
from .parser import parse_curve_event

# Constants
CONTRACT_ADDRESS = "0x52D34d8536350Cd997bCBD0b9E9d722452f341F5"


class CurveStream:
    def __init__(self, ws_url: str, debug: bool = False):
        self.ws_url = ws_url
        self.debug = debug
        self.event_types: List[EventType] = []
        self._subscription_id: Optional[str] = None
        self._w3: Optional[AsyncWeb3] = None
        self._topic_map: Dict[bytes, str] = {}  # topic -> event name mapping
        
    def subscribe(self, event_types: List[EventType] = None):
        """Set which events to subscribe to"""
        if event_types is None:
            event_types = [EventType.BUY, EventType.SELL]
        self.event_types = event_types
        
        
    async def events(self) -> AsyncIterator[Dict[str, Any]]:
        """Async iterator that yields parsed events"""
        # Create topics and mapping
        topics = []
        for event_type in self.event_types:
            topic = AsyncWeb3.keccak(text=event_type.value)
            topics.append(topic)
            self._topic_map[topic] = event_type.name
        
        if not topics:
            return
            
        # Connect and subscribe
        async with AsyncWeb3(WebSocketProvider(self.ws_url)) as w3:
            self._w3 = w3
            
            # Create filter
            filter_params = {
                "address": CONTRACT_ADDRESS,
                "topics": [topics]  # [[buy, sell]] for OR filter
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
                
                # Determine event type from topic0
                topic0 = log.get("topics", [])[0] if log.get("topics") else None
                if not topic0:
                    continue
                    
                # Convert to bytes if needed
                if hasattr(topic0, 'hex'):
                    topic0_bytes = topic0
                else:
                    topic0_bytes = bytes.fromhex(topic0.replace('0x', ''))
                
                # Get event name from topic
                event_name = self._topic_map.get(topic0_bytes)
                if not event_name:
                    continue
                
                # Parse and yield event
                event = parse_curve_event(log, event_name)
                if event:
                    yield event
    
