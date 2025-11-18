"""
Enterprise Stock Trading Framework - FastAPI Backend
Main application entry point
"""

import sys
import os
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import logging
import asyncio
from datetime import datetime
from typing import List, Dict, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_pipeline import DataPipeline
from multi_agent_system_part2 import create_analysis_workflow
from backtesting_engine import BacktestEngine, BacktestConfig, SMCFVGStrategy

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
pipeline: Optional[DataPipeline] = None
analysis_workflow = None
security = HTTPBearer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    global pipeline, analysis_workflow
    
    # Startup
    logger.info("🚀 Starting Enterprise Trading Framework Backend...")
    
    try:
        # Initialize data pipeline
        config = {
            'database_url': 'postgresql://trading_user:trading_password@postgres:5432/trading_framework',
            'redis_url': 'redis://redis:6379/0',
            'tradingview_webhook_secret': 'your-tradingview-webhook-secret'
        }
        
        pipeline = DataPipeline(config)
        await pipeline.initialize()
        
        # Initialize multi-agent workflow
        analysis_workflow = create_analysis_workflow()
        
        logger.info("✅ Backend initialized successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize backend: {e}")
        raise
    
    finally:
        # Shutdown
        if pipeline:
            await pipeline.shutdown()
        logger.info("🛑 Backend shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Enterprise Stock Trading Framework API",
    description="AI-powered multi-agent stock analysis with Smart Money Concepts",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


# Webhook endpoints
@app.post("/webhook/tradingview")
async def tradingview_webhook(webhook_data: Dict):
    """Receive TradingView webhook"""
    if not pipeline:
        raise HTTPException(status_code=500, detail="Pipeline not initialized")
    
    try:
        success = await pipeline.process_tradingview_webhook(webhook_data)
        if success:
            return {"status": "success", "message": "Webhook processed"}
        else:
            raise HTTPException(status_code=400, detail="Failed to process webhook")
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Analysis endpoints
@app.post("/api/v1/analysis/comprehensive/{symbol}")
async def comprehensive_analysis(symbol: str, timeframe: str = "daily", background_tasks: BackgroundTasks = BackgroundTasks()):
    """Run comprehensive multi-agent analysis"""
    if not analysis_workflow:
        raise HTTPException(status_code=500, detail="Analysis workflow not initialized")
    
    try:
        # Queue for background analysis
        background_tasks.add_task(run_comprehensive_analysis, symbol, timeframe)
        
        return {
            "status": "queued",
            "message": f"Comprehensive analysis queued for {symbol}",
            "symbol": symbol,
            "timeframe": timeframe
        }
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def run_comprehensive_analysis(symbol: str, timeframe: str):
    """Run comprehensive analysis in background"""
    try:
        # Fetch historical data
        if pipeline:
            candles = await pipeline.fetch_historical_data(symbol, timeframe, 30)
            
            if candles:
                # Convert to DataFrame format for analysis
                import pandas as pd
                
                data = []
                for candle in candles:
                    data.append({
                        'open': candle.open,
                        'high': candle.high,
                        'low': candle.low,
                        'close': candle.close,
                        'volume': candle.volume
                    })
                
                df = pd.DataFrame(data)
                
                # Initialize analysis state
                state = {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "ohlcv_data": df,
                    "current_date": datetime.now()
                }
                
                # Run multi-agent analysis
                result = analysis_workflow.invoke(state)
                
                # Store results in database
                if pipeline:
                    signal_data = {
                        'symbol': symbol,
                        'signal_type': result.get('final_signal', {}).get('signal', 'HOLD'),
                        'source': 'multi_agent_orchestrator',
                        'strength': result.get('final_signal', {}).get('strength', 0),
                        'confidence': result.get('confidence_score', 0),
                        'timeframe': timeframe,
                        'explanation': result.get('explanation', ''),
                        'raw_data': result
                    }
                    
                    await pipeline.db_manager.store_signal(signal_data)
                
                logger.info(f"✅ Comprehensive analysis completed for {symbol}")
                
    except Exception as e:
        logger.error(f"❌ Comprehensive analysis failed for {symbol}: {e}")


@app.get("/api/v1/analysis/results/{symbol}")
async def get_analysis_results(symbol: str, timeframe: str = "daily"):
    """Get latest analysis results"""
    if not pipeline:
        raise HTTPException(status_code=500, detail="Pipeline not initialized")
    
    try:
        signals = await pipeline.redis_manager.get_realtime_signals(symbol)
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "signals": signals,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Results error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Smart Money Concepts endpoints
@app.get("/api/v1/stocks/{symbol}/fvg/zones")
async def get_fvg_zones(symbol: str, timeframe: str = "daily"):
    """Get Fair Value Gap zones"""
    if not pipeline:
        raise HTTPException(status_code=500, detail="Pipeline not initialized")
    
    try:
        # Fetch recent data and analyze FVG
        candles = await pipeline.fetch_historical_data(symbol, timeframe, 30)
        if candles:
            fvg_zones = await pipeline.sm_processor.process_fvg_detection(symbol, timeframe, candles)
            return {
                "symbol": symbol,
                "timeframe": timeframe,
                "fvg_zones": fvg_zones,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {"symbol": symbol, "fvg_zones": []}
    except Exception as e:
        logger.error(f"FVG error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/stocks/{symbol}/market-structure")
async def get_market_structure(symbol: str, timeframe: str = "daily"):
    """Get market structure analysis"""
    if not pipeline:
        raise HTTPException(status_code=500, detail="Pipeline not initialized")
    
    try:
        candles = await pipeline.fetch_historical_data(symbol, timeframe, 30)
        if candles:
            structure = await pipeline.sm_processor.process_market_structure(symbol, timeframe, candles)
            return {
                "symbol": symbol,
                "timeframe": timeframe,
                "market_structure": structure,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {"symbol": symbol, "market_structure": {}}
    except Exception as e:
        logger.error(f"Market structure error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/stocks/{symbol}/volume-profile")
async def get_volume_profile(symbol: str, timeframe: str = "daily"):
    """Get volume profile analysis"""
    if not pipeline:
        raise HTTPException(status_code=500, detail="Pipeline not initialized")
    
    try:
        candles = await pipeline.fetch_historical_data(symbol, timeframe, 30)
        if candles:
            volume_profile = await pipeline.sm_processor.process_volume_profile(symbol, timeframe, candles)
            return {
                "symbol": symbol,
                "timeframe": timeframe,
                "volume_profile": volume_profile,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {"symbol": symbol, "volume_profile": {}}
    except Exception as e:
        logger.error(f"Volume profile error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Backtesting endpoints
@app.post("/api/v1/backtest/run")
async def run_backtest(backtest_config: Dict):
    """Run strategy backtest"""
    try:
        # Extract configuration
        strategy_config = backtest_config.get('strategy', {})
        backtest_params = backtest_config.get('backtest', {})
        
        # Create strategy
        strategy = SMCFVGStrategy(strategy_config)
        
        # Create backtest configuration
        config = BacktestConfig(
            initial_capital=backtest_params.get('initial_capital', 1000000),
            commission_per_trade=backtest_params.get('commission_per_trade', 20),
            slippage_percent=backtest_params.get('slippage_percent', 0.1),
            position_sizing_method=backtest_params.get('position_sizing_method', 'kelly'),
            position_size_percent=backtest_params.get('position_size_percent', 2.0),
            max_position_size=backtest_params.get('max_position_size', 100000),
            risk_per_trade=backtest_params.get('risk_per_trade', 2.0),
            benchmark_symbol=backtest_params.get('benchmark_symbol', 'NIFTY')
        )
        
        # Generate sample data (in production, fetch from database)
        import pandas as pd
        import numpy as np
        
        dates = pd.date_range(start='2022-01-01', end='2024-01-01', freq='D')
        np.random.seed(42)
        
        price_data = []
        price = 1000
        
        for i in range(len(dates)):
            change = np.random.normal(0.001, 0.02)
            price *= (1 + change)
            
            price_data.append({
                'open': price,
                'high': price * (1 + abs(np.random.normal(0, 0.01))),
                'low': price * (1 - abs(np.random.normal(0, 0.01))),
                'close': price,
                'volume': int(np.random.normal(1000000, 300000))
            })
        
        data = pd.DataFrame(price_data, index=dates)
        
        # Run backtest
        engine = BacktestEngine(config)
        result = await engine.run_backtest(strategy, data)
        
        # Convert result to dictionary
        result_dict = {
            "total_return": result.total_return,
            "annualized_return": result.annualized_return,
            "max_drawdown": result.max_drawdown,
            "sharpe_ratio": result.sharpe_ratio,
            "sortino_ratio": result.sortino_ratio,
            "win_rate": result.win_rate,
            "profit_factor": result.profit_factor,
            "total_trades": result.total_trades,
            "winning_trades": result.winning_trades,
            "losing_trades": result.losing_trades,
            "avg_trade_return": result.avg_trade_return,
            "avg_trade_duration": result.avg_trade_duration,
            "var_95": result.var_95,
            "calmar_ratio": result.calmar_ratio,
            "beta": result.beta,
            "alpha": result.alpha
        }
        
        return {
            "status": "completed",
            "backtest_id": f"bt_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "results": result_dict,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Backtest error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Market data endpoints
@app.get("/api/v1/stocks/{symbol}/price")
async def get_latest_price(symbol: str):
    """Get latest price for symbol"""
    if not pipeline:
        raise HTTPException(status_code=500, detail="Pipeline not initialized")
    
    try:
        price = await pipeline.redis_manager.get_latest_price(symbol)
        if price:
            return {
                "symbol": symbol,
                "price": price,
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Generate mock price if not in cache
            import random
            mock_price = random.uniform(100, 5000)
            await pipeline.redis_manager.cache_latest_price(symbol, mock_price)
            
            return {
                "symbol": symbol,
                "price": mock_price,
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        logger.error(f"Price error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/market/sector-momentum")
async def get_sector_momentum():
    """Get sector momentum analysis"""
    # Mock sector data
    sectors = {
        'Technology': {'score': 0.82, 'change': 2.5, 'fvg_count': 8},
        'Banking': {'score': 0.45, 'change': -1.2, 'fvg_count': 3},
        'Pharma': {'score': 0.67, 'change': 1.8, 'fvg_count': 5},
        'Energy': {'score': 0.78, 'change': 3.1, 'fvg_count': 7},
        'Metals': {'score': 0.33, 'change': -2.8, 'fvg_count': 2},
        'IT Services': {'score': 0.71, 'change': 1.5, 'fvg_count': 6}
    }
    
    return {
        "sectors": sectors,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/v1/signals/{symbol}")
async def get_signals(symbol: str):
    """Get latest signals for symbol"""
    if not pipeline:
        raise HTTPException(status_code=500, detail="Pipeline not initialized")
    
    try:
        signals = await pipeline.redis_manager.get_realtime_signals(symbol)
        return {
            "symbol": symbol,
            "signals": signals,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Signals error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Ideas generation endpoints
@app.get("/api/v1/ideas/swing-trading")
async def get_swing_trading_ideas():
    """Get swing trading ideas"""
    # Mock swing trading ideas
    ideas = [
        {
            'symbol': 'RELIANCE',
            'entry': 2845.50,
            'stop_loss': 2810.00,
            'target_1': 2920.00,
            'target_2': 2985.00,
            'rr_ratio': 2.8,
            'confidence': 85,
            'reasoning': 'Bullish FVG fill at 2845 with volume confirmation. Market structure shows higher highs.',
            'setup_type': 'FVG Fill + Volume Spike'
        },
        {
            'symbol': 'TCS',
            'entry': 3450.00,
            'stop_loss': 3410.00,
            'target_1': 3550.00,
            'target_2': 3620.00,
            'rr_ratio': 2.5,
            'confidence': 78,
            'reasoning': 'Ascending triangle breakout with high volume. Smart money accumulation detected.',
            'setup_type': 'Breakout + Smart Money'
        }
    ]
    
    return {
        "ideas": ideas,
        "type": "swing_trading",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/v1/ideas/long-term")
async def get_long_term_ideas():
    """Get long-term investment ideas"""
    # Mock long-term ideas
    ideas = [
        {
            'symbol': 'HDFCBANK',
            'current_price': 1658.20,
            'target_price': 1950.00,
            'upside_potential': 17.6,
            'quality_score': 82,
            'pe_ratio': 18.7,
            'roe': 16.8,
            'thesis': 'Leading private bank with strong ROE and improving asset quality.',
            'holding_period': '12-18 months'
        },
        {
            'symbol': 'INFY',
            'current_price': 1587.90,
            'target_price': 1850.00,
            'upside_potential': 16.5,
            'quality_score': 88,
            'pe_ratio': 25.1,
            'roe': 19.5,
            'thesis': 'IT sector leader with strong digital capabilities.',
            'holding_period': '18-24 months'
        }
    ]
    
    return {
        "ideas": ideas,
        "type": "long_term",
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
