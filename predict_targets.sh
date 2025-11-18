#!/bin/bash

# Multi-Horizon Price Target Predictor

if [ -z "$1" ]; then
    echo "Usage: ./predict_targets.sh TICKER"
    echo "Example: ./predict_targets.sh KPIGREEN"
    exit 1
fi

python3 multi_horizon_predictor.py "$1"
