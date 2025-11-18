#!/usr/bin/env python3
"""
Development startup script for Enterprise Stock Trading Framework
Starts all components in development mode without Docker
"""

import subprocess
import sys
import time
import os
import signal
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are available"""
    print("🔍 Checking dependencies...")
    
    # Check Python packages
    required_packages = [
        'fastapi', 'uvicorn', 'streamlit', 'pandas', 
        'numpy', 'plotly', 'asyncio', 'aiohttp'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {missing_packages}")
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install'
        ] + missing_packages)
        print("✅ Packages installed")

def create_sample_data():
    """Create sample data for development"""
    print("📊 Creating sample data...")
    
    # Create data directory
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Generate sample OHLCV data
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    
    # Generate sample data for popular stocks
    stocks = ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK']
    
    for symbol in stocks:
        dates = pd.date_range(start='2023-01-01', end=datetime.now(), freq='D')
        np.random.seed(hash(symbol) % 2**32)  # Consistent random data per symbol
        
        # Generate realistic price movements
        base_price = np.random.uniform(100, 3000)
        price_data = []
        
        for i, date in enumerate(dates):
            # Add trend and volatility
            trend = 0.0005 * (1 + hash(symbol) % 10)  # Different trends per symbol
            volatility = 0.02 * (1 + (hash(symbol) % 5) / 10)  # Different volatility
            
            change = np.random.normal(trend, volatility)
            base_price *= (1 + change)
            
            # Generate OHLC
            high = base_price * (1 + abs(np.random.normal(0, 0.01)))
            low = base_price * (1 - abs(np.random.normal(0, 0.01)))
            
            # Ensure high >= close >= open >= low
            open_price = np.random.uniform(low, high)
            close_price = np.random.uniform(low, high)
            
            if open_price > close_price:
                open_price, close_price = close_price, open_price
            
            volume = int(np.random.normal(1000000, 300000))
            
            price_data.append({
                'date': date,
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(close_price, 2),
                'volume': max(volume, 100000)
            })
        
        # Save to CSV
        df = pd.DataFrame(price_data)
        df.to_csv(data_dir / f"{symbol}_daily.csv", index=False)
    
    print("✅ Sample data created")

def start_backend():
    """Start the FastAPI backend"""
    print("🚀 Starting FastAPI backend...")
    
    # Set environment variables for development
    env = os.environ.copy()
    env.update({
        'DATABASE_URL': 'sqlite:///./trading_framework.db',  # Use SQLite for development
        'REDIS_URL': 'redis://localhost:6379/0',
        'SECRET_KEY': 'dev-secret-key',
        'DEBUG': 'true'
    })
    
    # Start backend in background
    backend_process = subprocess.Popen([
        sys.executable, 'backend/main.py'
    ], env=env, cwd=os.getcwd())
    
    return backend_process

def start_frontend():
    """Start the Streamlit frontend"""
    print("🖥️ Starting Streamlit frontend...")
    
    # Set environment variables for development
    env = os.environ.copy()
    env.update({
        'API_BASE_URL': 'http://localhost:8000',
        'BACKEND_URL': 'http://localhost:8000'
    })
    
    # Start frontend in background
    frontend_process = subprocess.Popen([
        sys.executable, '-m', 'streamlit', 'run', 'streamlit_app.py',
        '--server.port', '8501',
        '--server.address', '0.0.0.0',
        '--server.headless', 'true'
    ], env=env, cwd=os.getcwd())
    
    return frontend_process

def wait_for_services():
    """Wait for services to be ready"""
    print("⏳ Waiting for services to start...")
    
    import requests
    import time
    
    # Wait for backend
    backend_ready = False
    for i in range(30):  # Wait up to 30 seconds
        try:
            response = requests.get('http://localhost:8000/health', timeout=1)
            if response.status_code == 200:
                backend_ready = True
                print("✅ Backend is ready")
                break
        except:
            pass
        time.sleep(1)
    
    if not backend_ready:
        print("❌ Backend failed to start")
        return False
    
    # Wait for frontend
    frontend_ready = False
    for i in range(30):  # Wait up to 30 seconds
        try:
            response = requests.get('http://localhost:8501/_stcore/health', timeout=1)
            if response.status_code == 200:
                frontend_ready = True
                print("✅ Frontend is ready")
                break
        except:
            pass
        time.sleep(1)
    
    if not frontend_ready:
        print("❌ Frontend failed to start")
        return False
    
    return True

def main():
    """Main startup function"""
    print("🎯 Enterprise Stock Trading Framework - Development Mode")
    print("=" * 60)
    
    # Check dependencies
    check_dependencies()
    
    # Create sample data
    create_sample_data()
    
    # Start services
    processes = []
    
    try:
        # Start backend
        backend_process = start_backend()
        processes.append(backend_process)
        
        # Give backend time to start
        time.sleep(3)
        
        # Start frontend
        frontend_process = start_frontend()
        processes.append(frontend_process)
        
        # Wait for services to be ready
        if wait_for_services():
            print("\n🎉 All services started successfully!")
            print("\n📱 Access the application:")
            print("   • Streamlit UI: http://localhost:8501")
            print("   • FastAPI Backend: http://localhost:8000")
            print("   • API Documentation: http://localhost:8000/docs")
            print("\n🔧 Development Tips:")
            print("   • Use Ctrl+C to stop all services")
            print("   • Check logs for any errors")
            print("   • Sample data is available in ./data/")
            
            # Keep running
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Shutting down...")
                
        else:
            print("❌ Failed to start services")
            
    except Exception as e:
        print(f"❌ Error starting services: {e}")
    
    finally:
        # Clean up processes
        for process in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                try:
                    process.kill()
                except:
                    pass
        
        print("✅ All services stopped")

if __name__ == "__main__":
    main()
