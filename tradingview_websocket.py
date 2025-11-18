"""
TradingView WebSocket Integration for Real-time Data
Supports paid TradingView accounts with authentication
"""

import json
import websocket
import threading
import time
from typing import Dict, Callable, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TradingViewWebSocket:
    """
    WebSocket client for TradingView real-time data
    Requires paid TradingView account credentials
    """
    
    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        self.username = username
        self.password = password
        self.ws = None
        self.session_id = None
        self.chart_session = "cs_1"
        self.callbacks = {}
        self.price_data = {}
        self.connected = False
        
    def _generate_session_id(self):
        """Generate unique session ID"""
        import random
        import string
        return ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    
    def _send_message(self, func, args):
        """Send message to TradingView WebSocket"""
        if self.ws and self.connected:
            message = json.dumps({
                "m": func,
                "p": args
            })
            self.ws.send(f"~m~{len(message)}~m~{message}")
    
    def _on_message(self, ws, message):
        """Handle incoming WebSocket messages"""
        try:
            # Parse TradingView protocol
            if message.startswith("~m~"):
                parts = message.split("~m~")
                for i in range(1, len(parts), 2):
                    if i + 1 < len(parts):
                        data = json.loads(parts[i + 1])
                        self._process_message(data)
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def _process_message(self, data):
        """Process parsed message data"""
        if isinstance(data, dict):
            msg_type = data.get("m")
            
            if msg_type == "qsd":
                # Quote data update
                symbol_data = data.get("p", [])
                if len(symbol_data) >= 2:
                    symbol = symbol_data[0]
                    quote = symbol_data[1]
                    self.price_data[symbol] = quote
                    
                    # Trigger callbacks
                    if symbol in self.callbacks:
                        self.callbacks[symbol](quote)
    
    def _on_error(self, ws, error):
        """Handle WebSocket errors"""
        logger.error(f"WebSocket error: {error}")
        self.connected = False
    
    def _on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket close"""
        logger.info("WebSocket connection closed")
        self.connected = False
    
    def _on_open(self, ws):
        """Handle WebSocket open"""
        logger.info("WebSocket connection opened")
        self.connected = True
        
        # Initialize session
        self.session_id = self._generate_session_id()
        self._send_message("set_auth_token", [self.username or "unauthorized_user_token"])
        self._send_message("chart_create_session", [self.chart_session, ""])
        self._send_message("quote_create_session", [self.session_id])
    
    def connect(self):
        """Establish WebSocket connection"""
        websocket_url = "wss://data.tradingview.com/socket.io/websocket"
        
        self.ws = websocket.WebSocketApp(
            websocket_url,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
            on_open=self._on_open
        )
        
        # Run in separate thread
        wst = threading.Thread(target=self.ws.run_forever)
        wst.daemon = True
        wst.start()
        
        # Wait for connection
        timeout = 10
        start_time = time.time()
        while not self.connected and (time.time() - start_time) < timeout:
            time.sleep(0.1)
        
        return self.connected
    
    def subscribe(self, symbol: str, exchange: str = "NSE", callback: Optional[Callable] = None):
        """Subscribe to real-time updates for a symbol"""
        if not self.connected:
            logger.error("Not connected to WebSocket")
            return False
        
        full_symbol = f"{exchange}:{symbol}"
        
        if callback:
            self.callbacks[full_symbol] = callback
        
        # Subscribe to quote updates
        self._send_message("quote_add_symbols", [self.session_id, full_symbol])
        self._send_message("quote_fast_symbols", [self.session_id, full_symbol])
        
        logger.info(f"Subscribed to {full_symbol}")
        return True
    
    def unsubscribe(self, symbol: str, exchange: str = "NSE"):
        """Unsubscribe from symbol updates"""
        full_symbol = f"{exchange}:{symbol}"
        self._send_message("quote_remove_symbols", [self.session_id, full_symbol])
        
        if full_symbol in self.callbacks:
            del self.callbacks[full_symbol]
        
        logger.info(f"Unsubscribed from {full_symbol}")
    
    def get_price(self, symbol: str, exchange: str = "NSE") -> Optional[Dict]:
        """Get latest price data for symbol"""
        full_symbol = f"{exchange}:{symbol}"
        return self.price_data.get(full_symbol)
    
    def disconnect(self):
        """Close WebSocket connection"""
        if self.ws:
            self.ws.close()
        self.connected = False


# Singleton instance
_ws_instance = None

def get_tradingview_ws(username: Optional[str] = None, password: Optional[str] = None) -> TradingViewWebSocket:
    """Get or create TradingView WebSocket instance"""
    global _ws_instance
    
    if _ws_instance is None:
        _ws_instance = TradingViewWebSocket(username, password)
        _ws_instance.connect()
    
    return _ws_instance


if __name__ == "__main__":
    # Test WebSocket connection
    def on_price_update(data):
        print(f"Price update: {data}")
    
    ws = TradingViewWebSocket()
    if ws.connect():
        print("Connected to TradingView WebSocket")
        ws.subscribe("RELIANCE", "NSE", on_price_update)
        
        # Keep alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            ws.disconnect()
    else:
        print("Failed to connect")
