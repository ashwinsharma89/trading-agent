#!/usr/bin/env python3
"""
Enterprise Stock Trading Framework - Installation Script
Complete setup and installation guide
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def print_header():
    """Print installation header"""
    print("🎯 Enterprise Stock Trading Framework - Installation")
    print("=" * 60)
    print("AI-powered multi-agent stock analysis with Smart Money Concepts")
    print()

def check_system_requirements():
    """Check system requirements"""
    print("🔍 Checking system requirements...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major >= 3 and python_version.minor >= 8:
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"❌ Python {python_version.major}.{python_version.minor} detected. Python 3.8+ required.")
        return False
    
    # Check operating system
    os_name = platform.system()
    print(f"✅ Operating System: {os_name}")
    
    # Check available packages
    try:
        import pip
        print("✅ pip package manager available")
    except ImportError:
        print("❌ pip not available")
        return False
    
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    
    # Core dependencies
    core_packages = [
        'fastapi==0.104.1',
        'uvicorn[standard]==0.24.0',
        'streamlit==1.29.0',
        'pandas==2.1.4',
        'numpy==1.25.2',
        'plotly==5.17.0',
        'requests==2.31.0',
        'aiohttp==3.9.1',
        'python-dotenv==1.0.0'
    ]
    
    # Install packages
    for package in core_packages:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ {package}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            return False
    
    print("✅ All dependencies installed successfully")
    return True

def setup_configuration():
    """Set up configuration files"""
    print("\n⚙️ Setting up configuration...")
    
    # Create .env file if it doesn't exist
    env_file = Path('.env')
    if not env_file.exists():
        print("Creating .env file...")
        env_content = """# Database Configuration
DATABASE_URL=sqlite:///./trading_framework.db
REDIS_URL=redis://localhost:6379/0

# API Configuration
SECRET_KEY=dev-secret-key-change-in-production
DEBUG=true
LOG_LEVEL=INFO
ENVIRONMENT=development

# TradingView Configuration
TRADINGVIEW_WEBHOOK_SECRET=your-tradingview-webhook-secret

# External API Keys (Replace with your actual keys)
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-api-key
CLAUDE_API_KEY=your-claude-api-key

# Trading Configuration
DEFAULT_RISK_PER_TRADE=2.0
DEFAULT_POSITION_SIZE=2.5
MAX_POSITION_SIZE=10.0

# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
API_BASE_URL=http://localhost:8000
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ .env file created")
    else:
        print("✅ .env file already exists")
    
    # Create data directory
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    print("✅ Data directory created")
    
    # Create logs directory
    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)
    print("✅ Logs directory created")

def create_startup_scripts():
    """Create startup scripts"""
    print("\n🚀 Creating startup scripts...")
    
    # macOS/Linux startup script
    start_script = """#!/bin/bash
# Enterprise Stock Trading Framework - Startup Script

echo "🎯 Starting Enterprise Stock Trading Framework..."
echo "=============================================="

# Check if backend is already running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend already running on http://localhost:8000"
else
    echo "🚀 Starting FastAPI backend..."
    python3 simple_backend.py &
    BACKEND_PID=$!
    echo "Backend PID: $BACKEND_PID"
    
    # Wait for backend to start
    sleep 3
fi

# Check if frontend is already running
if curl -s http://localhost:8501/_stcore/health > /dev/null 2>&1; then
    echo "✅ Frontend already running on http://localhost:8501"
else
    echo "🖥️ Starting Streamlit frontend..."
    streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true &
    FRONTEND_PID=$!
    echo "Frontend PID: $FRONTEND_PID"
fi

echo ""
echo "🎉 Framework started successfully!"
echo "📱 Access the UI: http://localhost:8501"
echo "🔧 API Documentation: http://localhost:8000/docs"
echo "🏥 Health Check: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap 'echo "🛑 Stopping services..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit' INT
wait
"""
    
    with open('start_framework.sh', 'w') as f:
        f.write(start_script)
    
    # Make script executable
    os.chmod('start_framework.sh', 0o755)
    print("✅ macOS/Linux startup script created: start_framework.sh")
    
    # Windows startup script
    start_script_win = """@echo off
REM Enterprise Stock Trading Framework - Startup Script

echo 🎯 Starting Enterprise Stock Trading Framework...
echo ==============================================

REM Start FastAPI backend
echo 🚀 Starting FastAPI backend...
start /B python simple_backend.py

REM Wait for backend to start
timeout /t 3 /nobreak > nul

REM Start Streamlit frontend
echo 🖥️ Starting Streamlit frontend...
start /B streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true

echo.
echo 🎉 Framework started successfully!
echo 📱 Access the UI: http://localhost:8501
echo 🔧 API Documentation: http://localhost:8000/docs
echo 🏥 Health Check: http://localhost:8000/health
echo.
echo Press any key to stop services...
pause > nul
"""
    
    with open('start_framework.bat', 'w') as f:
        f.write(start_script_win)
    print("✅ Windows startup script created: start_framework.bat")

def create_desktop_shortcuts():
    """Create desktop shortcuts"""
    print("\n🖼️ Creating desktop shortcuts...")
    
    if platform.system() == "Darwin":  # macOS
        # Create macOS app
        app_dir = Path("EnterpriseTradingFramework.app")
        contents_dir = app_dir / "Contents"
        macos_dir = contents_dir / "MacOS"
        resources_dir = contents_dir / "Resources"
        
        contents_dir.mkdir(parents=True, exist_ok=True)
        macos_dir.mkdir(parents=True, exist_ok=True)
        resources_dir.mkdir(parents=True, exist_ok=True)
        
        # Info.plist
        info_plist = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>launch</string>
    <key>CFBundleIconFile</key>
    <string>icon.icns</string>
    <key>CFBundleName</key>
    <string>Enterprise Trading Framework</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
</dict>
</plist>
"""
        with open(contents_dir / "Info.plist", 'w') as f:
            f.write(info_plist)
        
        # Launch script
        launch_script = f"""#!/bin/bash
cd "{os.getcwd()}"
./start_framework.sh
"""
        with open(macos_dir / "launch", 'w') as f:
            f.write(launch_script)
        os.chmod(macos_dir / "launch", 0o755)
        
        print("✅ macOS app created: EnterpriseTradingFramework.app")
    
    elif platform.system() == "Windows":
        # Create Windows shortcut
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        path = os.path.join(desktop, "Enterprise Trading Framework.lnk")
        target = os.path.join(os.getcwd(), "start_framework.bat")
        wDir = os.getcwd()
        icon = target
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = target
        shortcut.WorkingDirectory = wDir
        shortcut.IconLocation = icon
        shortcut.save()
        print("✅ Windows desktop shortcut created")

def verify_installation():
    """Verify installation"""
    print("\n🔍 Verifying installation...")
    
    # Check if files exist
    required_files = [
        'simple_backend.py',
        'streamlit_app.py',
        'requirements.txt',
        '.env',
        'start_framework.sh'
    ]
    
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} missing")
            return False
    
    # Test imports
    try:
        import fastapi
        import streamlit
        import pandas
        import numpy
        import plotly
        print("✅ All packages imported successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    return True

def print_success_message():
    """Print success message"""
    print("\n🎉 Installation completed successfully!")
    print("=" * 60)
    print("\n📱 How to start the framework:")
    print("   • Method 1: ./start_framework.sh (macOS/Linux)")
    print("   • Method 2: start_framework.bat (Windows)")
    print("   • Method 3: python3 simple_backend.py (Backend only)")
    print("   • Method 4: streamlit run streamlit_app.py (Frontend only)")
    
    print("\n🌐 Access points:")
    print("   • Streamlit UI: http://localhost:8501")
    print("   • FastAPI Backend: http://localhost:8000")
    print("   • API Documentation: http://localhost:8000/docs")
    print("   • Health Check: http://localhost:8000/health")
    
    print("\n🎯 Features available:")
    print("   • 🧠 Multi-Agent Analysis System")
    print("   • 📊 Smart Money Concepts (FVG, Market Structure, Volume)")
    print("   • 🖥️ 7-Page Enterprise UI")
    print("   • 🧪 Backtesting Engine")
    print("   • 📡 Real-time API")
    print("   • 📈 Trading Ideas Generation")
    
    print("\n📚 Next steps:")
    print("   1. Run './start_framework.sh' to start the framework")
    print("   2. Open http://localhost:8501 in your browser")
    print("   3. Explore the 7 UI pages and features")
    print("   4. Test the API endpoints")
    print("   5. Customize the configuration in .env")
    
    print("\n🔧 For production deployment:")
    print("   • Install Docker and Docker Compose")
    print("   • Run 'docker-compose up -d'")
    print("   • Configure PostgreSQL and Redis")
    print("   • Set up external API keys")

def main():
    """Main installation function"""
    print_header()
    
    # Check system requirements
    if not check_system_requirements():
        print("\n❌ System requirements not met. Please install Python 3.8+")
        return
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Failed to install dependencies")
        return
    
    # Setup configuration
    setup_configuration()
    
    # Create startup scripts
    create_startup_scripts()
    
    # Create desktop shortcuts
    try:
        create_desktop_shortcuts()
    except Exception as e:
        print(f"⚠️ Could not create desktop shortcuts: {e}")
    
    # Verify installation
    if verify_installation():
        print_success_message()
    else:
        print("\n❌ Installation verification failed")

if __name__ == "__main__":
    main()
