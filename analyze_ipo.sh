#!/bin/bash

# IPO Analysis Script

if [ -z "$1" ]; then
    echo "Usage: ./analyze_ipo.sh TICKER [LISTING_DATE]"
    echo "Example: ./analyze_ipo.sh FIRSTCRY 2024-08-13"
    echo ""
    echo "Available IPOs:"
    echo "  FIRSTCRY  - FirstCry (2024-08-13)"
    echo "  ZOMATO    - Zomato (2021-07-23)"
    echo "  NYKAA     - Nykaa (2021-11-10)"
    echo "  PAYTM     - Paytm (2021-11-18)"
    exit 1
fi

TICKER=$1
LISTING_DATE=${2:-""}

python3 -c "
from ipo_analyzer import IPOAnalyzer

analyzer = IPOAnalyzer()
ticker = '${TICKER}.NS' if not '${TICKER}'.endswith('.NS') else '${TICKER}'
listing_date = '${LISTING_DATE}' if '${LISTING_DATE}' else None

print('\n' + '='*80)
print(f'🎯 IPO ANALYSIS: ${TICKER}')
print('='*80)

results = analyzer.analyze_ipo(ticker, listing_date)

if 'error' not in results:
    print('\n' + '='*80)
    print('✅ ANALYSIS COMPLETE')
    print('='*80)
else:
    print(f'\n❌ Error: {results[\"error\"]}')
"
