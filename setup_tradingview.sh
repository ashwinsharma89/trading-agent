#!/bin/bash

echo "🚀 TradingView Paid Account Setup"
echo "=================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Creating from .env.example..."
    cp .env.example .env
fi

echo "📝 Please add your TradingView credentials to .env file:"
echo ""
echo "Edit the following lines in .env:"
echo "  TRADINGVIEW_USERNAME=your_email@example.com"
echo "  TRADINGVIEW_PASSWORD=your_password"
echo ""
echo "Press Enter when done..."
read

# Test the connection
echo ""
echo "🧪 Testing TradingView connection..."
python3 data_provider.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Setup complete!"
    echo ""
    echo "📊 Starting Streamlit app..."
    streamlit run streamlit_app.py
else
    echo ""
    echo "❌ Connection test failed"
    echo "Please check your credentials in .env file"
fi
