"""
Data Pipeline for Enterprise Stock Trading Framework
TradingView Integration, Real-time Processing, and Smart Money Data Collection
"""

import asyncio
import aiohttp
import asyncpg
import redis.asyncio as redis
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import json
import logging
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataSource(Enum):
    """Data sources for market data"""
    TRADINGVIEW = "tradingview"
    YAHOO_FINANCE = "yahoo_finance"
    NSE_API = "nse_api"
    BSE_API = "bse_api"
    SCREENER_IN = "screener_in"


@dataclass
class OHLCVData:
    """OHLCV data structure"""
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    timeframe: str = "daily"
    
    # Smart money annotations
    is_fvg_candle: bool = False
    is_liquidity_grab: bool = False
    is_order_block: bool = False
    structure_break_type: Optional[str] = None


@dataclass
class TradingViewWebhook:
    """TradingView webhook data structure"""
    symbol: str
    timeframe: str
    action: str  # BUY, SELL, ALERT
    price: float
    volume: int
    timestamp: datetime
    indicator_data: Dict[str, Any]
    alert_name: str
    alert_message: str


class DatabaseManager:
    """Database operations manager"""
    
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.pool = None
    
    async def initialize(self):
        """Initialize database connection pool"""
        self.pool = await asyncpg.create_pool(
            self.db_url,
            min_size=5,
            max_size=20,
            command_timeout=60
        )
        logger.info("Database connection pool initialized")
    
    async def close(self):
        """Close database connections"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connections closed")
    
    async def store_ohlcv_data(self, data: OHLCVData) -> bool:
        """Store OHLCV data in TimescaleDB"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO ohlcv_data (
                        time, symbol, timeframe, open, high, low, close, volume,
                        is_fvg_candle, is_liquidity_grab, is_order_block_candle, 
                        structure_break_type, vwap, typical_price, weighted_close_price
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                    ON CONFLICT (time, symbol, timeframe) DO UPDATE SET
                        open = EXCLUDED.open,
                        high = EXCLUDED.high,
                        low = EXCLUDED.low,
                        close = EXCLUDED.close,
                        volume = EXCLUDED.volume,
                        is_fvg_candle = EXCLUDED.is_fvg_candle,
                        is_liquidity_grab = EXCLUDED.is_liquidity_grab,
                        is_order_block_candle = EXCLUDED.is_order_block_candle,
                        structure_break_type = EXCLUDED.structure_break_type
                """, 
                    data.timestamp, data.symbol, data.timeframe,
                    data.open, data.high, data.low, data.close, data.volume,
                    data.is_fvg_candle, data.is_liquidity_grab, data.is_order_block,
                    data.structure_break_type,
                    self._calculate_vwap(data), self._calculate_typical_price(data),
                    self._calculate_weighted_close(data)
                )
                return True
        except Exception as e:
            logger.error(f"Error storing OHLCV data: {e}")
            return False
    
    def _calculate_vwap(self, data: OHLCVData) -> float:
        """Calculate VWAP (simplified - would need historical data)"""
        return (data.high + data.low + data.close) / 3
    
    def _calculate_typical_price(self, data: OHLCVData) -> float:
        """Calculate typical price"""
        return (data.high + data.low + data.close) / 3
    
    def _calculate_weighted_close(self, data: OHLCVData) -> float:
        """Calculate weighted close price"""
        return (data.high + data.low + 2 * data.close) / 4
    
    async def get_latest_ohlcv(self, symbol: str, timeframe: str, limit: int = 100) -> List[OHLCVData]:
        """Get latest OHLCV data for a symbol"""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT time, symbol, timeframe, open, high, low, close, volume,
                           is_fvg_candle, is_liquidity_grab, is_order_block_candle,
                           structure_break_type
                    FROM ohlcv_data
                    WHERE symbol = $1 AND timeframe = $2
                    ORDER BY time DESC
                    LIMIT $3
                """, symbol, timeframe, limit)
                
                return [
                    OHLCVData(
                        symbol=row['symbol'],
                        timestamp=row['time'],
                        open=row['open'],
                        high=row['high'],
                        low=row['low'],
                        close=row['close'],
                        volume=row['volume'],
                        timeframe=row['timeframe'],
                        is_fvg_candle=row['is_fvg_candle'],
                        is_liquidity_grab=row['is_liquidity_grab'],
                        is_order_block=row['is_order_block_candle'],
                        structure_break_type=row['structure_break_type']
                    )
                    for row in rows
                ]
        except Exception as e:
            logger.error(f"Error getting latest OHLCV data: {e}")
            return []
    
    async def store_signal(self, signal_data: Dict[str, Any]) -> bool:
        """Store trading signal in database"""
        try:
            async with self.pool.acquire() as conn:
                # Get stock_id
                stock_id = await conn.fetchval(
                    "SELECT id FROM stocks WHERE symbol = $1",
                    signal_data['symbol']
                )
                
                if not stock_id:
                    logger.warning(f"Stock {signal_data['symbol']} not found in database")
                    return False
                
                await conn.execute("""
                    INSERT INTO signals (
                        stock_id, signal_type, source, strength, confidence,
                        timeframe, raw_data, explanation, created_at, expires_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """,
                    stock_id,
                    signal_data['signal_type'],
                    signal_data['source'],
                    signal_data.get('strength'),
                    signal_data.get('confidence'),
                    signal_data.get('timeframe'),
                    json.dumps(signal_data.get('raw_data', {})),
                    signal_data.get('explanation'),
                    datetime.now(),
                    datetime.now() + timedelta(hours=24)  # Signals expire in 24 hours
                )
                return True
        except Exception as e:
            logger.error(f"Error storing signal: {e}")
            return False


class RedisManager:
    """Redis operations manager for caching and real-time data"""
    
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis = None
    
    async def initialize(self):
        """Initialize Redis connection"""
        self.redis = redis.from_url(self.redis_url)
        await self.redis.ping()
        logger.info("Redis connection initialized")
    
    async def close(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
            logger.info("Redis connection closed")
    
    async def cache_latest_price(self, symbol: str, price: float, ttl: int = 300):
        """Cache latest price with TTL"""
        key = f"price:{symbol}"
        await self.redis.setex(key, ttl, price)
    
    async def get_latest_price(self, symbol: str) -> Optional[float]:
        """Get latest price from cache"""
        key = f"price:{symbol}"
        price = await self.redis.get(key)
        return float(price) if price else None
    
    async def store_realtime_signal(self, signal_data: Dict[str, Any]):
        """Store real-time signal in Redis"""
        key = f"signal:{signal_data['symbol']}:{signal_data['source']}"
        await self.redis.setex(
            key, 
            3600,  # 1 hour TTL
            json.dumps(signal_data)
        )
        
        # Also add to signals stream
        await self.redis.xadd(
            "signals_stream",
            signal_data,
            maxlen=10000  # Keep last 10k signals
        )
    
    async def get_realtime_signals(self, symbol: str = None) -> List[Dict[str, Any]]:
        """Get real-time signals from Redis"""
        if symbol:
            # Get specific symbol signals
            keys = await self.redis.keys(f"signal:{symbol}:*")
        else:
            # Get all recent signals
            keys = await self.redis.keys("signal:*")
        
        signals = []
        for key in keys:
            data = await self.redis.get(key)
            if data:
                signals.append(json.loads(data))
        
        return signals
    
    async def add_to_watchlist_cache(self, user_id: int, symbols: List[str]):
        """Cache user watchlist"""
        key = f"watchlist:{user_id}"
        await self.redis.setex(key, 1800, json.dumps(symbols))  # 30 min TTL
    
    async def get_watchlist_cache(self, user_id: int) -> List[str]:
        """Get user watchlist from cache"""
        key = f"watchlist:{user_id}"
        data = await self.redis.get(key)
        return json.loads(data) if data else []


class TradingViewClient:
    """TradingView API and Webhook client"""
    
    def __init__(self, webhook_secret: str):
        self.webhook_secret = webhook_secret
        self.base_url = "https://scanner.tradingview.com"
    
    async def get_screener_data(self, symbols: List[str], indicators: List[str]) -> Dict[str, Any]:
        """Get data from TradingView screener API"""
        try:
            async with aiohttp.ClientSession() as session:
                # Prepare screener request
                payload = {
                    "symbols": {"tickers": [f"NSE:{symbol}" for symbol in symbols]},
                    "columns": indicators
                }
                
                async with session.post(
                    f"{self.base_url}/global/scan",
                    json=payload,
                    headers={"User-Agent": "TradingFramework/1.0"}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_screener_response(data, symbols)
                    else:
                        logger.error(f"TradingView API error: {response.status}")
                        return {}
        except Exception as e:
            logger.error(f"Error fetching TradingView screener data: {e}")
            return {}
    
    def _parse_screener_response(self, data: Dict[str, Any], symbols: List[str]) -> Dict[str, Any]:
        """Parse TradingView screener response"""
        parsed_data = {}
        
        if not data.get('data'):
            return parsed_data
        
        for item in data['data']:
            symbol = item.get('s', '').replace('NSE:', '')
            if symbol in symbols:
                values = item.get('d', [])
                parsed_data[symbol] = {
                    'price': values[0] if len(values) > 0 else None,
                    'volume': values[1] if len(values) > 1 else None,
                    'rsi': values[2] if len(values) > 2 else None,
                    'macd': values[3] if len(values) > 3 else None,
                    # Add more indicators as needed
                }
        
        return parsed_data
    
    def parse_webhook(self, webhook_data: Dict[str, Any]) -> Optional[TradingViewWebhook]:
        """Parse TradingView webhook data"""
        try:
            # Validate webhook secret
            if webhook_data.get('secret') != self.webhook_secret:
                logger.warning("Invalid webhook secret")
                return None
            
            return TradingViewWebhook(
                symbol=webhook_data['symbol'],
                timeframe=webhook_data.get('timeframe', 'daily'),
                action=webhook_data['action'],
                price=float(webhook_data['price']),
                volume=int(webhook_data.get('volume', 0)),
                timestamp=datetime.fromisoformat(webhook_data['timestamp']),
                indicator_data=webhook_data.get('indicators', {}),
                alert_name=webhook_data.get('alert_name', ''),
                alert_message=webhook_data.get('message', '')
            )
        except Exception as e:
            logger.error(f"Error parsing webhook: {e}")
            return None


class SmartMoneyDataProcessor:
    """Process smart money concepts data"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    async def process_fvg_detection(self, symbol: str, timeframe: str, candles: List[OHLCVData]) -> List[Dict[str, Any]]:
        """Detect Fair Value Gaps from candle data"""
        fvg_zones = []
        
        for i in range(2, len(candles)):
            candle_1 = candles[i-2]
            candle_2 = candles[i-1]
            
            # Bullish FVG detection
            if candle_1.high < candle_2.low:
                fvg = {
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'zone_type': 'bullish_fvg',
                    'high_price': candle_2.low,
                    'low_price': candle_1.high,
                    'midpoint': (candle_2.low + candle_1.high) / 2,
                    'strength': self._calculate_fvg_strength(candle_1, candle_2),
                    'created_at': datetime.now()
                }
                fvg_zones.append(fvg)
            
            # Bearish FVG detection
            elif candle_1.low > candle_2.high:
                fvg = {
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'zone_type': 'bearish_fvg',
                    'high_price': candle_1.low,
                    'low_price': candle_2.high,
                    'midpoint': (candle_1.low + candle_2.high) / 2,
                    'strength': self._calculate_fvg_strength(candle_1, candle_2),
                    'created_at': datetime.now()
                }
                fvg_zones.append(fvg)
        
        return fvg_zones
    
    def _calculate_fvg_strength(self, candle_1: OHLCVData, candle_2: OHLCVData) -> str:
        """Calculate FVG strength based on volume and gap size"""
        avg_volume = (candle_1.volume + candle_2.volume) / 2
        gap_size = abs(candle_1.high - candle_2.low) / candle_1.close
        
        if avg_volume > 1000000 and gap_size > 0.02:
            return "strong"
        elif avg_volume > 500000 and gap_size > 0.01:
            return "medium"
        else:
            return "weak"
    
    async def process_market_structure(self, symbol: str, timeframe: str, candles: List[OHLCVData]) -> Dict[str, Any]:
        """Analyze market structure (HH/HL, LL/LH)"""
        if len(candles) < 10:
            return {}
        
        # Find swing highs and lows
        swing_highs = []
        swing_lows = []
        
        for i in range(2, len(candles) - 2):
            candle = candles[i]
            
            # Swing high detection
            if (candle.high > candles[i-1].high and 
                candle.high > candles[i-2].high and
                candle.high > candles[i+1].high and 
                candle.high > candles[i+2].high):
                swing_highs.append(candle.high)
            
            # Swing low detection
            if (candle.low < candles[i-1].low and 
                candle.low < candles[i-2].low and
                candle.low < candles[i+1].low and 
                candle.low < candles[i+2].low):
                swing_lows.append(candle.low)
        
        # Determine trend
        trend = "sideways"
        if len(swing_highs) >= 2 and len(swing_lows) >= 2:
            if swing_highs[-1] > swing_highs[-2] and swing_lows[-1] > swing_lows[-2]:
                trend = "bullish"
            elif swing_highs[-1] < swing_highs[-2] and swing_lows[-1] < swing_lows[-2]:
                trend = "bearish"
        
        return {
            'symbol': symbol,
            'timeframe': timeframe,
            'trend': trend,
            'swing_highs': swing_highs[-5:],  # Last 5 swing highs
            'swing_lows': swing_lows[-5:],    # Last 5 swing lows
            'key_levels': {
                'resistance': sorted(swing_highs[-3:], reverse=True) if swing_highs else [],
                'support': sorted(swing_lows[-3:]) if swing_lows else []
            },
            'created_at': datetime.now()
        }
    
    async def process_volume_profile(self, symbol: str, timeframe: str, candles: List[OHLCVData]) -> Dict[str, Any]:
        """Calculate volume profile from candle data"""
        if not candles:
            return {}
        
        # Group candles by price levels
        price_volume_map = {}
        
        for candle in candles:
            price_level = round(candle.close, 2)
            if price_level not in price_volume_map:
                price_volume_map[price_level] = 0
            price_volume_map[price_level] += candle.volume
        
        if not price_volume_map:
            return {}
        
        # Find Point of Control (highest volume)
        poc = max(price_volume_map.keys(), key=lambda x: price_volume_map[x])
        
        # Calculate Value Area (simplified - 70% of total volume)
        total_volume = sum(price_volume_map.values())
        target_volume = total_volume * 0.7
        
        sorted_prices = sorted(price_volume_map.items(), key=lambda x: x[1], reverse=True)
        accumulated_volume = 0
        va_prices = []
        
        for price, volume in sorted_prices:
            va_prices.append(price)
            accumulated_volume += volume
            if accumulated_volume >= target_volume:
                break
        
        value_area_high = max(va_prices) if va_prices else poc
        value_area_low = min(va_prices) if va_prices else poc
        
        return {
            'symbol': symbol,
            'timeframe': timeframe,
            'poc': poc,
            'value_area_high': value_area_high,
            'value_area_low': value_area_low,
            'volume_levels': price_volume_map,
            'total_volume': total_volume,
            'volume_gap': self._detect_volume_gap(price_volume_map),
            'created_at': datetime.now()
        }
    
    def _detect_volume_gap(self, price_volume_map: Dict[float, int]) -> bool:
        """Detect significant volume gaps"""
        volumes = list(price_volume_map.values())
        if len(volumes) < 3:
            return False
        
        avg_volume = np.mean(volumes)
        
        # Look for areas with very low volume between high volume areas
        for i in range(1, len(volumes) - 1):
            if (volumes[i] < avg_volume * 0.1 and 
                volumes[i-1] > avg_volume and 
                volumes[i+1] > avg_volume):
                return True
        
        return False


class DataPipeline:
    """Main data pipeline orchestrator"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_manager = DatabaseManager(config['database_url'])
        self.redis_manager = RedisManager(config['redis_url'])
        self.tv_client = TradingViewClient(config['tradingview_webhook_secret'])
        self.sm_processor = SmartMoneyDataProcessor(self.db_manager)
        
        # Active subscriptions and tasks
        self.active_subscriptions = {}
        self.background_tasks = []
    
    async def initialize(self):
        """Initialize all components"""
        await self.db_manager.initialize()
        await self.redis_manager.initialize()
        logger.info("Data pipeline initialized")
    
    async def shutdown(self):
        """Shutdown all components"""
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        await self.db_manager.close()
        await self.redis_manager.close()
        logger.info("Data pipeline shutdown complete")
    
    async def process_tradingview_webhook(self, webhook_data: Dict[str, Any]) -> bool:
        """Process incoming TradingView webhook"""
        try:
            # Parse webhook
            webhook = self.tv_client.parse_webhook(webhook_data)
            if not webhook:
                return False
            
            logger.info(f"Processing webhook: {webhook.symbol} - {webhook.action}")
            
            # Store in Redis for real-time processing
            signal_data = {
                'symbol': webhook.symbol,
                'action': webhook.action,
                'price': webhook.price,
                'timestamp': webhook.timestamp.isoformat(),
                'source': 'tradingview_webhook',
                'indicator_data': webhook.indicator_data,
                'alert_name': webhook.alert_name
            }
            
            await self.redis_manager.store_realtime_signal(signal_data)
            
            # Queue for multi-agent analysis
            await self._queue_for_analysis(webhook.symbol, webhook.timeframe)
            
            return True
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return False
    
    async def _queue_for_analysis(self, symbol: str, timeframe: str):
        """Queue symbol for multi-agent analysis"""
        # This would integrate with the Celery task queue
        # For now, we'll store a simple flag in Redis
        key = f"analysis_queue:{symbol}:{timeframe}"
        await self.redis_manager.setex(key, 3600, datetime.now().isoformat())
    
    async def fetch_historical_data(self, symbol: str, timeframe: str, days: int = 30) -> List[OHLCVData]:
        """Fetch historical data for analysis"""
        try:
            # Try to get from database first
            existing_data = await self.db_manager.get_latest_ohlcv(symbol, timeframe, days)
            
            if len(existing_data) >= days:
                logger.info(f"Retrieved {len(existing_data)} candles from database for {symbol}")
                return existing_data
            
            # Fetch from external API (mock implementation)
            logger.info(f"Fetching historical data for {symbol} from external API")
            new_data = await self._fetch_from_external_api(symbol, timeframe, days)
            
            # Store in database
            for candle in new_data:
                await self.db_manager.store_ohlcv_data(candle)
            
            return new_data
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            return []
    
    async def _fetch_from_external_api(self, symbol: str, timeframe: str, days: int) -> List[OHLCVData]:
        """Fetch data from external API (mock implementation)"""
        # This would integrate with Yahoo Finance, NSE/BSE APIs, etc.
        # For now, return mock data
        
        mock_data = []
        base_date = datetime.now() - timedelta(days=days)
        base_price = 500 + np.random.randn() * 100
        
        for i in range(days):
            date = base_date + timedelta(days=i)
            
            # Generate mock OHLCV data
            open_price = base_price + np.random.randn() * 10
            high = open_price + abs(np.random.randn() * 5)
            low = open_price - abs(np.random.randn() * 5)
            close = low + (high - low) * np.random.random()
            volume = int(1000000 + np.random.randn() * 500000)
            
            candle = OHLCVData(
                symbol=symbol,
                timestamp=date,
                open=round(open_price, 2),
                high=round(high, 2),
                low=round(low, 2),
                close=round(close, 2),
                volume=volume,
                timeframe=timeframe
            )
            
            mock_data.append(candle)
            base_price = close
        
        return mock_data
    
    async def run_smart_money_analysis(self, symbol: str, timeframe: str = "daily"):
        """Run smart money analysis on a symbol"""
        try:
            logger.info(f"Running smart money analysis for {symbol}")
            
            # Get historical data
            candles = await self.fetch_historical_data(symbol, timeframe, 30)
            if not candles:
                logger.warning(f"No data available for {symbol}")
                return
            
            # Process FVG detection
            fvg_zones = await self.sm_processor.process_fvg_detection(symbol, timeframe, candles)
            for fvg in fvg_zones:
                await self._store_fvg_zone(fvg)
            
            # Process market structure
            structure = await self.sm_processor.process_market_structure(symbol, timeframe, candles)
            if structure:
                await self._store_market_structure(structure)
            
            # Process volume profile
            volume_profile = await self.sm_processor.process_volume_profile(symbol, timeframe, candles)
            if volume_profile:
                await self._store_volume_profile(volume_profile)
            
            logger.info(f"Smart money analysis completed for {symbol}")
            
        except Exception as e:
            logger.error(f"Error in smart money analysis: {e}")
    
    async def _store_fvg_zone(self, fvg_data: Dict[str, Any]):
        """Store FVG zone in database"""
        try:
            async with self.db_manager.pool.acquire() as conn:
                stock_id = await conn.fetchval(
                    "SELECT id FROM stocks WHERE symbol = $1",
                    fvg_data['symbol']
                )
                
                if stock_id:
                    await conn.execute("""
                        INSERT INTO fvg_zones (
                            stock_id, timeframe, zone_type, high_price, low_price,
                            midpoint, strength, mitigated, created_at, valid_until
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    """,
                        stock_id, fvg_data['timeframe'], fvg_data['zone_type'],
                        fvg_data['high_price'], fvg_data['low_price'], fvg_data['midpoint'],
                        fvg_data['strength'], False, fvg_data['created_at'],
                        fvg_data['created_at'] + timedelta(days=7)
                    )
        except Exception as e:
            logger.error(f"Error storing FVG zone: {e}")
    
    async def _store_market_structure(self, structure_data: Dict[str, Any]):
        """Store market structure in database"""
        try:
            async with self.db_manager.pool.acquire() as conn:
                stock_id = await conn.fetchval(
                    "SELECT id FROM stocks WHERE symbol = $1",
                    structure_data['symbol']
                )
                
                if stock_id:
                    await conn.execute("""
                        INSERT INTO market_structure (
                            stock_id, timeframe, trend, swing_highs, swing_lows,
                            key_levels, created_at, valid_until
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    """,
                        stock_id, structure_data['timeframe'], structure_data['trend'],
                        structure_data['swing_highs'], structure_data['swing_lows'],
                        json.dumps(structure_data['key_levels']), structure_data['created_at'],
                        structure_data['created_at'] + timedelta(days=7)
                    )
        except Exception as e:
            logger.error(f"Error storing market structure: {e}")
    
    async def _store_volume_profile(self, profile_data: Dict[str, Any]):
        """Store volume profile in database"""
        try:
            async with self.db_manager.pool.acquire() as conn:
                stock_id = await conn.fetchval(
                    "SELECT id FROM stocks WHERE symbol = $1",
                    profile_data['symbol']
                )
                
                if stock_id:
                    await conn.execute("""
                        INSERT INTO volume_profiles (
                            stock_id, timeframe, poc, value_area_high, value_area_low,
                            volume_levels, volume_gap, accumulation_phase, total_volume,
                            created_at, valid_until
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                    """,
                        stock_id, profile_data['timeframe'], profile_data['poc'],
                        profile_data['value_area_high'], profile_data['value_area_low'],
                        json.dumps(profile_data['volume_levels']), profile_data['volume_gap'],
                        False, profile_data['total_volume'], profile_data['created_at'],
                        profile_data['created_at'] + timedelta(days=1)
                    )
        except Exception as e:
            logger.error(f"Error storing volume profile: {e}")
    
    async def start_real_time_monitoring(self, symbols: List[str]):
        """Start real-time monitoring for symbols"""
        logger.info(f"Starting real-time monitoring for {len(symbols)} symbols")
        
        for symbol in symbols:
            if symbol not in self.active_subscriptions:
                task = asyncio.create_task(self._monitor_symbol(symbol))
                self.active_subscriptions[symbol] = task
                self.background_tasks.append(task)
    
    async def _monitor_symbol(self, symbol: str):
        """Monitor a single symbol for real-time updates"""
        while True:
            try:
                # Fetch latest data
                latest_data = await self.fetch_historical_data(symbol, "daily", 5)
                
                if latest_data:
                    latest_candle = latest_data[-1]
                    
                    # Cache latest price
                    await self.redis_manager.cache_latest_price(symbol, latest_candle.close)
                    
                    # Run smart money analysis periodically
                    await self.run_smart_money_analysis(symbol, "daily")
                
                # Wait before next update (5 minutes)
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"Error monitoring {symbol}: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry


# FastAPI integration
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel

app = FastAPI(title="Trading Framework Data Pipeline")

# Global pipeline instance
pipeline = None

class WebhookData(BaseModel):
    symbol: str
    action: str
    price: float
    timestamp: str
    secret: str
    timeframe: str = "daily"
    volume: int = 0
    indicators: Dict[str, Any] = {}
    alert_name: str = ""
    message: str = ""

@app.on_event("startup")
async def startup_event():
    global pipeline
    config = {
        'database_url': 'postgresql://trading_user:trading_password@localhost:5432/trading_framework',
        'redis_url': 'redis://localhost:6379/0',
        'tradingview_webhook_secret': 'your-webhook-secret'
    }
    pipeline = DataPipeline(config)
    await pipeline.initialize()

@app.on_event("shutdown")
async def shutdown_event():
    global pipeline
    if pipeline:
        await pipeline.shutdown()

@app.post("/webhook/tradingview")
async def tradingview_webhook(webhook_data: WebhookData):
    """Receive TradingView webhook"""
    if not pipeline:
        raise HTTPException(status_code=500, detail="Pipeline not initialized")
    
    success = await pipeline.process_tradingview_webhook(webhook_data.dict())
    if success:
        return {"status": "success", "message": "Webhook processed"}
    else:
        raise HTTPException(status_code=400, detail="Failed to process webhook")

@app.post("/analyze/{symbol}")
async def analyze_symbol(symbol: str, timeframe: str = "daily", background_tasks: BackgroundTasks = BackgroundTasks()):
    """Trigger analysis for a symbol"""
    if not pipeline:
        raise HTTPException(status_code=500, detail="Pipeline not initialized")
    
    # Queue for background analysis
    background_tasks.add_task(pipeline.run_smart_money_analysis, symbol, timeframe)
    
    return {"status": "queued", "message": f"Analysis queued for {symbol}"}

@app.get("/signals/{symbol}")
async def get_signals(symbol: str):
    """Get latest signals for a symbol"""
    if not pipeline:
        raise HTTPException(status_code=500, detail="Pipeline not initialized")
    
    signals = await pipeline.redis_manager.get_realtime_signals(symbol)
    return {"symbol": symbol, "signals": signals}

@app.get("/price/{symbol}")
async def get_latest_price(symbol: str):
    """Get latest price for a symbol"""
    if not pipeline:
        raise HTTPException(status_code=500, detail="Pipeline not initialized")
    
    price = await pipeline.redis_manager.get_latest_price(symbol)
    if price:
        return {"symbol": symbol, "price": price, "timestamp": datetime.now().isoformat()}
    else:
        raise HTTPException(status_code=404, detail="Price not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
