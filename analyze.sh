#!/bin/bash
if [ -z "$1" ]; then
    echo "Usage: ./analyze.sh TICKER"
    echo "Example: ./analyze.sh KPIGREEN"
    exit 1
fi
python3 analyze_with_learning.py "$1"
