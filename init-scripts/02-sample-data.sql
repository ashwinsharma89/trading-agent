-- Sample data insertion for development and testing

-- Insert sample stocks
INSERT INTO stocks (symbol, name, sector, industry, exchange, market_cap_category) VALUES
('RELIANCE', 'Reliance Industries Ltd', 'Energy', 'Oil & Gas', 'NSE', 'large_cap'),
('TCS', 'Tata Consultancy Services', 'Technology', 'IT Services', 'NSE', 'large_cap'),
('HDFCBANK', 'HDFC Bank Ltd', 'Banking', 'Private Bank', 'NSE', 'large_cap'),
('INFY', 'Infosys Ltd', 'Technology', 'IT Services', 'NSE', 'large_cap'),
('ICICIBANK', 'ICICI Bank Ltd', 'Banking', 'Private Bank', 'NSE', 'large_cap'),
('HINDUNILVR', 'Hindustan Unilever Ltd', 'FMCG', 'Consumer Goods', 'NSE', 'large_cap'),
('SBIN', 'State Bank of India', 'Banking', 'Public Bank', 'NSE', 'large_cap'),
('BHARTIARTL', 'Bharti Airtel Ltd', 'Telecom', 'Wireless', 'NSE', 'large_cap'),
('KOTAKBANK', 'Kotak Mahindra Bank Ltd', 'Banking', 'Private Bank', 'NSE', 'large_cap'),
('LT', 'Larsen & Toubro Ltd', 'Engineering', 'Construction', 'NSE', 'large_cap'),
('WIPRO', 'Wipro Ltd', 'Technology', 'IT Services', 'NSE', 'large_cap'),
('AXISBANK', 'Axis Bank Ltd', 'Banking', 'Private Bank', 'NSE', 'large_cap'),
('MARUTI', 'Maruti Suzuki India Ltd', 'Auto', 'Passenger Vehicles', 'NSE', 'large_cap'),
('SUNPHARMA', 'Sun Pharmaceutical Industries Ltd', 'Pharma', 'Pharmaceuticals', 'NSE', 'large_cap'),
('TITAN', 'Titan Company Ltd', 'Consumer Durables', 'Jewellery', 'NSE', 'large_cap'),
('BAJFINANCE', 'Bajaj Finance Ltd', 'Finance', 'NBFC', 'NSE', 'large_cap'),
('M&M', 'Mahindra & Mahindra Ltd', 'Auto', 'Commercial Vehicles', 'NSE', 'large_cap'),
('HCLTECH', 'HCL Technologies Ltd', 'Technology', 'IT Services', 'NSE', 'large_cap'),
('NTPC', 'NTPC Ltd', 'Energy', 'Power Generation', 'NSE', 'large_cap'),
('ONGC', 'Oil & Natural Gas Corporation Ltd', 'Energy', 'Oil & Gas', 'NSE', 'large_cap')
ON CONFLICT (symbol) DO NOTHING;

-- Insert sample users
INSERT INTO users (email, password_hash, role, first_name, last_name) VALUES
('admin@tradingframework.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6ukx.LrUpm', 'admin', 'Admin', 'User'),
('analyst1@company.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6ukx.LrUpm', 'analyst', 'John', 'Smith'),
('trader1@company.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6ukx.LrUpm', 'trader', 'Jane', 'Doe')
ON CONFLICT (email) DO NOTHING;

-- Create sample watchlists
INSERT INTO watchlists (user_id, name, description, is_default) VALUES
(2, 'My Top Picks', 'High conviction trading ideas', true),
(2, 'Long-term Holdings', 'Fundamentally strong companies', false),
(3, 'Day Trading', 'Liquid stocks for intraday trading', true)
ON CONFLICT (user_id, name) DO NOTHING;

-- Add stocks to watchlists
INSERT INTO watchlist_stocks (watchlist_id, stock_id, notes) VALUES
-- My Top Picks
(1, (SELECT id FROM stocks WHERE symbol = 'RELIANCE'), 'Energy giant with strong FVG setup'),
(1, (SELECT id FROM stocks WHERE symbol = 'TCS'), 'IT leader with bullish structure'),
(1, (SELECT id FROM stocks WHERE symbol = 'HDFCBANK'), 'Banking sector leader'),
-- Long-term Holdings
(2, (SELECT id FROM stocks WHERE symbol = 'HINDUNILVR'), 'FMCG leader with consistent growth'),
(2, (SELECT id FROM stocks WHERE symbol = 'SUNPHARMA'), 'Pharma sector with strong pipeline'),
(2, (SELECT id FROM stocks WHERE symbol = 'BAJFINANCE'), 'NBFC leader with high ROE'),
-- Day Trading
(3, (SELECT id FROM stocks WHERE symbol = 'RELIANCE'), 'High volume, good for intraday'),
(3, (SELECT id FROM stocks WHERE symbol = 'TCS'), 'Tech stock with good volatility'),
(3, (SELECT id FROM stocks WHERE symbol = 'ICICIBANK'), 'Banking stock with liquidity')
ON CONFLICT (watchlist_id, stock_id) DO NOTHING;

-- Insert sample fundamental data
INSERT INTO fundamental_data (stock_id, report_date, quarter, year, revenue, profit, eps, book_value, pe_ratio, pb_ratio, roe_percent, roce_percent, debt_to_equity, current_ratio, interest_coverage, dividend_yield, quality_score, quality_grade) VALUES
-- RELIANCE
((SELECT id FROM stocks WHERE symbol = 'RELIANCE'), '2024-09-30', 2, 2024, 2450000, 185000, 28.5, 950, 22.5, 3.2, 18.5, 15.2, 0.4, 1.8, 8.5, 1.2, 82, 'A'),
-- TCS
((SELECT id FROM stocks WHERE symbol = 'TCS'), '2024-09-30', 2, 2024, 1850000, 125000, 45.2, 320, 28.3, 8.5, 24.1, 32.8, 0.1, 2.5, 15.2, 1.5, 88, 'A+'),
-- HDFCBANK
((SELECT id FROM stocks WHERE symbol = 'HDFCBANK'), '2024-09-30', 2, 2024, 650000, 95000, 18.7, 280, 18.7, 2.8, 16.8, 12.5, 0.8, 1.9, 6.8, 0.8, 75, 'A')
ON CONFLICT (stock_id, report_date) DO NOTHING;

-- Insert sample FVG zones
INSERT INTO fvg_zones (stock_id, timeframe, zone_type, high_price, low_price, midpoint, strength, mitigated, created_at, valid_until) VALUES
((SELECT id FROM stocks WHERE symbol = 'RELIANCE'), 'daily', 'bullish_fvg', 2875.00, 2850.00, 2862.50, 'strong', false, NOW(), NOW() + INTERVAL '7 days'),
((SELECT id FROM stocks WHERE symbol = 'TCS'), 'daily', 'bearish_fvg', 3475.00, 3450.00, 3462.50, 'medium', false, NOW(), NOW() + INTERVAL '7 days'),
((SELECT id FROM stocks WHERE symbol = 'HDFCBANK'), 'daily', 'bullish_fvg', 1665.00, 1650.00, 1657.50, 'strong', false, NOW(), NOW() + INTERVAL '7 days')
ON CONFLICT DO NOTHING;

-- Insert sample market structure data
INSERT INTO market_structure (stock_id, timeframe, trend, swing_highs, swing_lows, key_levels, created_at, valid_until) VALUES
((SELECT id FROM stocks WHERE symbol = 'RELIANCE'), 'daily', 'bullish', ARRAY[2950, 2900, 2850], ARRAY[2750, 2700, 2650], '{"resistance": [2950, 2900], "support": [2750, 2700]}', NOW(), NOW() + INTERVAL '7 days'),
((SELECT id FROM stocks WHERE symbol = 'TCS'), 'daily', 'bullish', ARRAY[3500, 3450, 3400], ARRAY[3300, 3250, 3200], '{"resistance": [3500, 3450], "support": [3300, 3250]}', NOW(), NOW() + INTERVAL '7 days'),
((SELECT id FROM stocks WHERE symbol = 'HDFCBANK'), 'daily', 'sideways', ARRAY[1680, 1670, 1660], ARRAY[1640, 1630, 1620], '{"resistance": [1680, 1670], "support": [1640, 1630]}', NOW(), NOW() + INTERVAL '7 days')
ON CONFLICT DO NOTHING;

-- Insert sample volume profiles
INSERT INTO volume_profiles (stock_id, timeframe, poc, value_area_high, value_area_low, volume_levels, volume_gap, accumulation_phase, total_volume, created_at, valid_until) VALUES
((SELECT id FROM stocks WHERE symbol = 'RELIANCE'), 'daily', 2865.00, 2890.00, 2835.00, '{"2865": 5000000, "2870": 4500000, "2860": 4200000}', true, true, 25000000, NOW(), NOW() + INTERVAL '1 day'),
((SELECT id FROM stocks WHERE symbol = 'TCS'), 'daily', 3462.50, 3480.00, 3445.00, '{"3462.5": 3500000, "3465": 3200000, "3460": 3000000}', false, true, 18000000, NOW(), NOW() + INTERVAL '1 day'),
((SELECT id FROM stocks WHERE symbol = 'HDFCBANK'), 'daily', 1657.50, 1670.00, 1645.00, '{"1657.5": 2800000, "1660": 2600000, "1655": 2400000}', false, false, 15000000, NOW(), NOW() + INTERVAL '1 day')
ON CONFLICT DO NOTHING;

-- Insert sample signals
INSERT INTO signals (stock_id, signal_type, source, strength, confidence, timeframe, raw_data, explanation, created_at, expires_at) VALUES
((SELECT id FROM stocks WHERE symbol = 'RELIANCE'), 'BUY', 'smc_analysis', 85, 78, 'daily', '{"fvg_detected": true, "volume_confirmation": true, "structure_alignment": true}', 'Bullish FVG fill with volume confirmation and market structure alignment', NOW(), NOW() + INTERVAL '24 hours'),
((SELECT id FROM stocks WHERE symbol = 'TCS'), 'BUY', 'technical', 72, 65, 'daily', '{"rsi": 58, "macd": "bullish_crossover", "sma_cross": "golden_cross"}', 'Golden cross with bullish MACD crossover', NOW(), NOW() + INTERVAL '24 hours'),
((SELECT id FROM stocks WHERE symbol = 'HDFCBANK'), 'HOLD', 'fundamental', 60, 55, 'daily', '{"pe_ratio": 18.7, "roe": 16.8, "debt_to_equity": 0.8}', 'Fair valuation with strong fundamentals', NOW(), NOW() + INTERVAL '24 hours')
ON CONFLICT DO NOTHING;

-- Insert sample aggregated signals
INSERT INTO aggregated_signals (stock_id, final_signal, confidence, strength, agent_weights, explanation, requires_human_review, created_at, expires_at) VALUES
((SELECT id FROM stocks WHERE symbol = 'RELIANCE'), 'BUY', 78, 85, '{"smc": 0.3, "technical": 0.25, "fundamental": 0.2, "volume": 0.15, "risk": 0.1}', 'Strong BUY signal with high confidence from Smart Money Concepts analysis. FVG fill setup with volume confirmation and bullish market structure.', false, NOW(), NOW() + INTERVAL '24 hours'),
((SELECT id FROM stocks WHERE symbol = 'TCS'), 'BUY', 68, 72, '{"technical": 0.35, "smc": 0.25, "fundamental": 0.2, "volume": 0.15, "risk": 0.05}', 'BUY signal based on technical indicators and fundamental strength. Golden cross pattern with good risk-reward ratio.', false, NOW(), NOW() + INTERVAL '24 hours'),
((SELECT id FROM stocks WHERE symbol = 'HDFCBANK'), 'HOLD', 55, 60, '{"fundamental": 0.4, "technical": 0.3, "smc": 0.15, "volume": 0.1, "risk": 0.05}', 'HOLD recommendation. Fair valuation with strong fundamentals but sideways market structure suggests waiting for better entry.', false, NOW(), NOW() + INTERVAL '24 hours')
ON CONFLICT DO NOTHING;

-- Insert sample risk metrics
INSERT INTO risk_metrics (stock_id, timeframe, historical_volatility, atr, atr_percent, beta, volatility_percentile, risk_rating, entry_price, stop_loss, target_1, target_2, risk_percent, rr_ratio_1, rr_ratio_2, trade_quality, max_allocation_percent, kelly_fraction, recommended_shares, created_at, valid_until) VALUES
((SELECT id FROM stocks WHERE symbol = 'RELIANCE'), 'daily', 0.28, 45.50, 0.0159, 1.2, 65, 'MEDIUM', 2850.75, 2810.00, 2920.00, 2985.00, 1.43, 1.53, 2.75, 'GOOD', 2.5, 0.025, 88, NOW(), NOW() + INTERVAL '7 days'),
((SELECT id FROM stocks WHERE symbol = 'TCS'), 'daily', 0.25, 52.30, 0.0151, 1.1, 58, 'MEDIUM', 3456.40, 3410.00, 3550.00, 3620.00, 1.34, 1.68, 2.89, 'GOOD', 2.5, 0.022, 73, NOW(), NOW() + INTERVAL '7 days'),
((SELECT id FROM stocks WHERE symbol = 'HDFCBANK'), 'daily', 0.22, 28.90, 0.0174, 0.9, 45, 'LOW', 1658.20, 1625.00, 1720.00, 1780.00, 2.00, 2.15, 3.84, 'EXCELLENT', 3.0, 0.018, 182, NOW(), NOW() + INTERVAL '7 days')
ON CONFLICT DO NOTHING;

-- Insert sample portfolios
INSERT INTO portfolios (user_id, name, description, initial_capital, current_capital) VALUES
(2, 'My Trading Portfolio', 'Active trading portfolio with focus on large-cap stocks', 1000000, 1025000),
(3, 'Day Trading Account', 'High-frequency trading portfolio', 500000, 512000)
ON CONFLICT (user_id, name) DO NOTHING;

-- Insert sample portfolio positions
INSERT INTO portfolio_positions (portfolio_id, stock_id, quantity, avg_cost_price, current_price, unrealized_pnl) VALUES
(1, (SELECT id FROM stocks WHERE symbol = 'RELIANCE'), 100, 2750.00, 2850.75, 10075),
(1, (SELECT id FROM stocks WHERE symbol = 'TCS'), 50, 3400.00, 3456.40, 2820),
(1, (SELECT id FROM stocks WHERE symbol = 'HDFCBANK'), 200, 1620.00, 1658.20, 7640),
(2, (SELECT id FROM stocks WHERE symbol = 'ICICIBANK'), 150, 980.00, 1025.50, 6825),
(2, (SELECT id FROM stocks WHERE symbol = 'KOTAKBANK'), 100, 1850.00, 1890.25, 4025)
ON CONFLICT (portfolio_id, stock_id) DO NOTHING;

-- Insert sample alert rules
INSERT INTO alert_rules (user_id, stock_id, rule_name, rule_type, conditions, is_active, notification_channels) VALUES
(2, (SELECT id FROM stocks WHERE symbol = 'RELIANCE'), 'RELIANCE FVG Fill Alert', 'fvg', '{"fvg_type": "bullish", "volume_confirmation": true, "min_strength": "medium"}', true, '["email"]'),
(2, (SELECT id FROM stocks WHERE symbol = 'TCS'), 'TCS Breakout Alert', 'price', '{"price_above": 3500, "volume_multiplier": 1.5}', true, '["email", "push"]'),
(3, (SELECT id FROM stocks WHERE symbol = 'HDFCBANK'), 'HDFCBANK Volume Spike', 'volume', '{"volume_multiplier": 2.0, "price_change_min": 1.0}', true, '["email"]')
ON CONFLICT DO NOTHING;

-- Insert sample backtest strategies
INSERT INTO backtest_strategies (name, description, user_id, strategy_config, is_active) VALUES
('SMC FVG Strategy v1', 'Smart Money Concepts strategy with FVG detection and volume confirmation', 2, '{"fvg_strength": "medium", "volume_multiplier": 1.5, "risk_reward_ratio": 2.5, "position_sizing_method": "kelly"}', true),
('Momentum Breakout Strategy', 'Technical momentum strategy with breakout detection', 2, '{"rsi_threshold": 50, "volume_multiplier": 1.2, "lookback_period": 20, "risk_reward_ratio": 2.0}', true),
('Value Investing Strategy', 'Fundamental value investing with quality filters', 2, '{"max_pe": 20, "min_roe": 15, "max_debt_equity": 1.0, "holding_period": 90}', false)
ON CONFLICT DO NOTHING;

-- Insert sample backtest results
INSERT INTO backtest_results (strategy_id, stock_id, start_date, end_date, initial_capital, final_capital, total_return, annualized_return, max_drawdown, sharpe_ratio, sortino_ratio, win_rate, profit_factor, avg_trade_return, total_trades, winning_trades, losing_trades, avg_trade_duration, volatility, var_95, detailed_results) VALUES
(1, (SELECT id FROM stocks WHERE symbol = 'RELIANCE'), '2022-01-01', '2024-01-01', 1000000, 1458000, 45.8, 18.3, -12.5, 1.85, 2.45, 68.5, 2.15, 2.85, 156, 107, 49, 8.5, 0.18, -25000, '{"avg_win": 5.2, "avg_loss": -2.4, "largest_win": 15.8, "largest_loss": -8.2}'),
(2, (SELECT id FROM stocks WHERE symbol = 'TCS'), '2022-01-01', '2024-01-01', 1000000, 1325000, 32.5, 14.2, -10.8, 1.62, 2.18, 62.3, 1.85, 2.15, 142, 88, 54, 6.2, 0.15, -22000, '{"avg_win": 4.8, "avg_loss": -2.6, "largest_win": 12.5, "largest_loss": -7.8}'),
(3, (SELECT id FROM stocks WHERE symbol = 'HDFCBANK'), '2022-01-01', '2024-01-01', 1000000, 1185000, 18.5, 8.8, -8.2, 1.25, 1.75, 58.7, 1.45, 1.85, 98, 57, 41, 45.0, 0.12, -18000, '{"avg_win": 3.2, "avg_loss": -2.2, "largest_win": 8.5, "largest_loss": -6.2}')
ON CONFLICT DO NOTHING;

COMMIT;
