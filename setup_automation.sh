#!/bin/bash

# Setup Automation Script
# Configures cron jobs for automated evaluation and retraining

echo "🤖 AUTOMATION SETUP"
echo "=================================================================="
echo ""

# Check if running on macOS or Linux
if [[ "$OSTYPE" == "darwin"* ]]; then
    SCHEDULER="launchd"
    echo "Detected: macOS (using launchd)"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    SCHEDULER="cron"
    echo "Detected: Linux (using cron)"
else
    echo "❌ Unsupported OS: $OSTYPE"
    exit 1
fi

# Get project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Project directory: $PROJECT_DIR"
echo ""

# Setup for macOS (launchd)
if [ "$SCHEDULER" == "launchd" ]; then
    echo "Setting up launchd jobs..."
    
    PLIST_DIR="$HOME/Library/LaunchAgents"
    mkdir -p "$PLIST_DIR"
    
    # Daily evaluation job
    cat > "$PLIST_DIR/com.trading.daily-evaluation.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.trading.daily-evaluation</string>
    <key>ProgramArguments</key>
    <array>
        <string>$PROJECT_DIR/venv/bin/python3</string>
        <string>$PROJECT_DIR/automation/scheduler.py</string>
        <string>--run-now</string>
        <string>evaluation</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>18</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>$PROJECT_DIR/logs/evaluation.log</string>
    <key>StandardErrorPath</key>
    <string>$PROJECT_DIR/logs/evaluation.error.log</string>
</dict>
</plist>
EOF
    
    # Weekly retraining job
    cat > "$PLIST_DIR/com.trading.weekly-retraining.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.trading.weekly-retraining</string>
    <key>ProgramArguments</key>
    <array>
        <string>$PROJECT_DIR/venv/bin/python3</string>
        <string>$PROJECT_DIR/automation/scheduler.py</string>
        <string>--run-now</string>
        <string>retraining</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Weekday</key>
        <integer>0</integer>
        <key>Hour</key>
        <integer>20</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>$PROJECT_DIR/logs/retraining.log</string>
    <key>StandardErrorPath</key>
    <string>$PROJECT_DIR/logs/retraining.error.log</string>
</dict>
</plist>
EOF
    
    # Load jobs
    launchctl load "$PLIST_DIR/com.trading.daily-evaluation.plist"
    launchctl load "$PLIST_DIR/com.trading.weekly-retraining.plist"
    
    echo "✅ launchd jobs configured"
    echo "   - Daily evaluation: 6:00 PM"
    echo "   - Weekly retraining: Sunday 8:00 PM"

# Setup for Linux (cron)
elif [ "$SCHEDULER" == "cron" ]; then
    echo "Setting up cron jobs..."
    
    # Create cron entries
    CRON_ENTRIES="
# Trading Framework Automation
0 18 * * * cd $PROJECT_DIR && ./venv/bin/python3 automation/scheduler.py --run-now evaluation >> logs/evaluation.log 2>&1
0 20 * * 0 cd $PROJECT_DIR && ./venv/bin/python3 automation/scheduler.py --run-now retraining >> logs/retraining.log 2>&1
"
    
    # Add to crontab
    (crontab -l 2>/dev/null; echo "$CRON_ENTRIES") | crontab -
    
    echo "✅ Cron jobs configured"
    echo "   - Daily evaluation: 6:00 PM"
    echo "   - Weekly retraining: Sunday 8:00 PM"
fi

# Create logs directory
mkdir -p "$PROJECT_DIR/logs"

echo ""
echo "=================================================================="
echo "✅ AUTOMATION SETUP COMPLETE!"
echo "=================================================================="
echo ""
echo "Scheduled jobs:"
echo "  1. Daily Evaluation - 6:00 PM (evaluates 30+ day predictions)"
echo "  2. Weekly Retraining - Sunday 8:00 PM (optimizes agent weights)"
echo ""
echo "Logs location: $PROJECT_DIR/logs/"
echo ""
echo "Manual controls:"
echo "  Run evaluation now:  python3 automation/scheduler.py --run-now evaluation"
echo "  Run retraining now:  python3 automation/scheduler.py --run-now retraining"
echo "  Run as daemon:       python3 automation/scheduler.py --daemon"
echo ""

if [ "$SCHEDULER" == "launchd" ]; then
    echo "Manage jobs:"
    echo "  List jobs:   launchctl list | grep trading"
    echo "  Stop job:    launchctl unload ~/Library/LaunchAgents/com.trading.*.plist"
    echo "  Start job:   launchctl load ~/Library/LaunchAgents/com.trading.*.plist"
elif [ "$SCHEDULER" == "cron" ]; then
    echo "Manage jobs:"
    echo "  View crontab:   crontab -l"
    echo "  Edit crontab:   crontab -e"
    echo "  Remove jobs:    crontab -e (then delete the lines)"
fi

echo ""
