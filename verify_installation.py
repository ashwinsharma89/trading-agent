#!/usr/bin/env python3
"""
Enterprise Stock Trading Framework - Installation Verification
"""

import sys
import subprocess
import requests
from pathlib import Path

def check_dependencies():
    """Check if all dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'fastapi', 'uvicorn', 'streamlit', 'pandas', 
        'numpy', 'plotly', 'requests', 'aiohttp', 'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'python-dotenv':
                __import__('dotenv')
            else:
                __import__(package.replace('-', '_').replace('.', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    return len(missing_packages) == 0

def check_files():
    """Check if required files exist"""
    print("\n📁 Checking required files...")
    
    required_files = [
        'simple_backend.py',
        'streamlit_app.py',
        'start_framework.sh',
        '.env'
    ]
    
    missing_files = []
    
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            missing_files.append(file)
            print(f"❌ {file}")
    
    return len(missing_files) == 0

def check_services():
    """Check if services are running"""
    print("\n🚀 Checking services...")
    
    # Check backend
    try:
        response = requests.get('http://localhost:8000/health', timeout=2)
        if response.status_code == 200:
            print("✅ FastAPI Backend (http://localhost:8000)")
            backend_running = True
        else:
            print("❌ FastAPI Backend not responding correctly")
            backend_running = False
    except:
        print("❌ FastAPI Backend not running")
        backend_running = False
    
    # Check frontend
    try:
        response = requests.get('http://localhost:8501/_stcore/health', timeout=2)
        if response.status_code == 200:
            print("✅ Streamlit Frontend (http://localhost:8501)")
            frontend_running = True
        else:
            print("❌ Streamlit Frontend not responding correctly")
            frontend_running = False
    except:
        print("❌ Streamlit Frontend not running")
        frontend_running = False
    
    return backend_running and frontend_running

def test_api_endpoints():
    """Test key API endpoints"""
    print("\n🧪 Testing API endpoints...")
    
    endpoints = [
        ('Health Check', '/health'),
        ('Stocks List', '/api/v1/stocks'),
        ('RELIANCE Price', '/api/v1/stocks/RELIANCE/price'),
        ('RELIANCE FVG Zones', '/api/v1/stocks/RELIANCE/fvg/zones'),
        ('Market Momentum', '/api/v1/market/sector-momentum'),
        ('Swing Ideas', '/api/v1/ideas/swing-trading')
    ]
    
    for name, endpoint in endpoints:
        try:
            response = requests.get(f'http://localhost:8000{endpoint}', timeout=2)
            if response.status_code == 200:
                print(f"✅ {name}")
            else:
                print(f"❌ {name} (Status: {response.status_code})")
        except Exception as e:
            print(f"❌ {name} (Error: {e})")

def print_installation_status():
    """Print overall installation status"""
    print("\n" + "="*60)
    print("🎯 ENTERPRISE STOCK TRADING FRAMEWORK - INSTALLATION STATUS")
    print("="*60)
    
    deps_ok = check_dependencies()
    files_ok = check_files()
    
    if deps_ok and files_ok:
        print("\n✅ Installation Complete!")
        print("\n🚀 To start the framework:")
        print("   ./start_framework.sh")
        print("\n📱 Access points:")
        print("   • Streamlit UI: http://localhost:8501")
        print("   • FastAPI Backend: http://localhost:8000")
        print("   • API Documentation: http://localhost:8000/docs")
        
        # Check if services are running
        if check_services():
            print("\n🎉 All services are running!")
            test_api_endpoints()
        else:
            print("\n⚠️ Services are not running. Use './start_framework.sh' to start them.")
    else:
        print("\n❌ Installation incomplete!")
        if not deps_ok:
            print("   • Some dependencies are missing")
        if not files_ok:
            print("   • Some required files are missing")

if __name__ == "__main__":
    print_installation_status()
