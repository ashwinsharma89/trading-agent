#!/bin/bash
# Enterprise Stock Trading Framework - Startup Script

echo "🎯 Enterprise Stock Trading Framework - Starting..."
echo "=================================================="

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
echo "🧠 Smart Money Features Active:"
echo "   • Fair Value Gap (FVG) Detection"
echo "   • Market Structure Analysis"
echo "   • Volume Profile Analysis"
echo "   • Multi-Agent Signal Generation"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap 'echo "🛑 Stopping services..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo "✅ All services stopped"; exit' INT
wait
