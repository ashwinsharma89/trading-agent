-- Enterprise Stock Trading Framework - Database Schema
-- PostgreSQL with TimescaleDB extension for time-series data

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- ============================================================================
-- POSTGRESQL SCHEMAS (Structured Data)
-- ============================================================================

-- Core tables for user management and metadata
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'analyst', -- admin, analyst, trader
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    preferences JSONB DEFAULT '{}',
    last_login TIMESTAMP WITH TIME ZONE
);

CREATE TABLE stocks (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    industry VARCHAR(100),
    exchange VARCHAR(20) NOT NULL, -- NSE, BSE
    market_cap_category VARCHAR(20), -- large_cap, mid_cap, small_cap
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

CREATE TABLE watchlists (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_default BOOLEAN DEFAULT FALSE,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, name)
);

CREATE TABLE watchlist_stocks (
    id SERIAL PRIMARY KEY,
    watchlist_id INTEGER REFERENCES watchlists(id) ON DELETE CASCADE,
    stock_id INTEGER REFERENCES stocks(id) ON DELETE CASCADE,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    notes TEXT,
    UNIQUE(watchlist_id, stock_id)
);

-- Signals and analysis results
CREATE TABLE signals (
    id SERIAL PRIMARY KEY,
    stock_id INTEGER REFERENCES stocks(id),
    signal_type VARCHAR(50) NOT NULL, -- BUY, SELL, HOLD
    source VARCHAR(100) NOT NULL, -- technical, fundamental, smc, volume, pattern, risk, orchestrator
    strength DECIMAL(5,2), -- 0-100
    confidence DECIMAL(5,2), -- 0-100
    timeframe VARCHAR(20), -- 15min, 1hr, 4hr, daily, weekly
    raw_data JSONB NOT NULL, -- Complete agent output
    explanation TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE aggregated_signals (
    id SERIAL PRIMARY KEY,
    stock_id INTEGER REFERENCES stocks(id),
    final_signal VARCHAR(50) NOT NULL,
    confidence DECIMAL(5,2) NOT NULL,
    strength DECIMAL(5,2) NOT NULL,
    agent_weights JSONB NOT NULL,
    explanation TEXT,
    requires_human_review BOOLEAN DEFAULT FALSE,
    reviewed_by INTEGER REFERENCES users(id),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE
);

-- Smart Money Concepts specific tables
CREATE TABLE market_structure (
    id SERIAL PRIMARY KEY,
    stock_id INTEGER REFERENCES stocks(id),
    timeframe VARCHAR(20) NOT NULL,
    trend VARCHAR(20) NOT NULL, -- bullish, bearish, sideways
    swing_highs DECIMAL(12,2)[], -- Array of swing high prices
    swing_lows DECIMAL(12,2)[], -- Array of swing low prices
    last_bos DECIMAL(12,2), -- Last break of structure level
    last_choch DECIMAL(12,2), -- Last change of character level
    key_levels JSONB, -- Support and resistance levels
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    valid_until TIMESTAMP WITH TIME ZONE
);

CREATE TABLE fvg_zones (
    id SERIAL PRIMARY KEY,
    stock_id INTEGER REFERENCES stocks(id),
    timeframe VARCHAR(20) NOT NULL,
    zone_type VARCHAR(20) NOT NULL, -- bullish_fvg, bearish_fvg
    high_price DECIMAL(12,2) NOT NULL,
    low_price DECIMAL(12,2) NOT NULL,
    midpoint DECIMAL(12,2) NOT NULL,
    strength VARCHAR(20) NOT NULL, -- strong, medium, weak
    mitigated BOOLEAN DEFAULT FALSE,
    mitigation_time TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    valid_until TIMESTAMP WITH TIME ZONE
);

CREATE TABLE order_blocks (
    id SERIAL PRIMARY KEY,
    stock_id INTEGER REFERENCES stocks(id),
    timeframe VARCHAR(20) NOT NULL,
    block_type VARCHAR(20) NOT NULL, -- buy, sell
    high_price DECIMAL(12,2) NOT NULL,
    low_price DECIMAL(12,2) NOT NULL,
    strength DECIMAL(5,2) NOT NULL, -- 0-100
    volume_confirmation BIGINT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    valid_until TIMESTAMP WITH TIME ZONE
);

CREATE TABLE liquidity_zones (
    id SERIAL PRIMARY KEY,
    stock_id INTEGER REFERENCES stocks(id),
    timeframe VARCHAR(20) NOT NULL,
    zone_type VARCHAR(20) NOT NULL, -- liquidity_highs, liquidity_lows
    price_level DECIMAL(12,2) NOT NULL,
    strength INTEGER NOT NULL, -- Number of equal highs/lows
    sweep_probability DECIMAL(5,2), -- 0-100
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    valid_until TIMESTAMP WITH TIME ZONE
);

-- Volume analysis tables
CREATE TABLE volume_profiles (
    id SERIAL PRIMARY KEY,
    stock_id INTEGER REFERENCES stocks(id),
    timeframe VARCHAR(20) NOT NULL,
    poc DECIMAL(12,2) NOT NULL, -- Point of Control
    value_area_high DECIMAL(12,2) NOT NULL,
    value_area_low DECIMAL(12,2) NOT NULL,
    volume_levels JSONB NOT NULL, -- Price -> Volume mapping
    volume_gap BOOLEAN DEFAULT FALSE,
    accumulation_phase BOOLEAN DEFAULT FALSE,
    total_volume BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    valid_until TIMESTAMP WITH TIME ZONE
);

-- Pattern recognition tables
CREATE TABLE detected_patterns (
    id SERIAL PRIMARY KEY,
    stock_id INTEGER REFERENCES stocks(id),
    timeframe VARCHAR(20) NOT NULL,
    pattern_name VARCHAR(100) NOT NULL,
    pattern_type VARCHAR(50) NOT NULL, -- bullish_reversal, bearish_reversal, continuation, indecision
    pattern_category VARCHAR(50) NOT NULL, -- candlestick, chart, smc
    reliability DECIMAL(5,2) NOT NULL, -- 0-100
    signal_strength DECIMAL(5,2) NOT NULL, -- 0-100
    pattern_data JSONB NOT NULL, -- Pattern-specific data
    confirmed BOOLEAN DEFAULT FALSE,
    target_price DECIMAL(12,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    valid_until TIMESTAMP WITH TIME ZONE
);

-- Fundamental data tables
CREATE TABLE fundamental_data (
    id SERIAL PRIMARY KEY,
    stock_id INTEGER REFERENCES stocks(id),
    report_date DATE NOT NULL,
    quarter INTEGER, -- 1,2,3,4 for quarterly data
    year INTEGER NOT NULL,
    
    -- Financial metrics
    revenue DECIMAL(15,2),
    profit DECIMAL(15,2),
    eps DECIMAL(10,2),
    book_value DECIMAL(10,2),
    
    -- Ratios
    pe_ratio DECIMAL(8,2),
    pb_ratio DECIMAL(8,2),
    roe_percent DECIMAL(5,2),
    roce_percent DECIMAL(5,2),
    debt_to_equity DECIMAL(8,2),
    current_ratio DECIMAL(5,2),
    interest_coverage DECIMAL(5,2),
    dividend_yield DECIMAL(5,2),
    price_to_sales DECIMAL(8,2),
    ev_ebitda DECIMAL(8,2),
    
    -- Growth metrics
    revenue_growth_yoy DECIMAL(5,2),
    profit_growth_yoy DECIMAL(5,2),
    eps_growth_yoy DECIMAL(5,2),
    
    -- Quality score
    quality_score DECIMAL(5,2),
    quality_grade VARCHAR(5),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(stock_id, report_date)
);

-- Risk assessment tables
CREATE TABLE risk_metrics (
    id SERIAL PRIMARY KEY,
    stock_id INTEGER REFERENCES stocks(id),
    timeframe VARCHAR(20) NOT NULL,
    
    -- Volatility metrics
    historical_volatility DECIMAL(8,4),
    atr DECIMAL(12,2),
    atr_percent DECIMAL(5,4),
    beta DECIMAL(5,2),
    volatility_percentile DECIMAL(5,2),
    risk_rating VARCHAR(20), -- LOW, MEDIUM, HIGH
    
    -- Risk-reward analysis
    entry_price DECIMAL(12,2),
    stop_loss DECIMAL(12,2),
    target_1 DECIMAL(12,2),
    target_2 DECIMAL(12,2),
    risk_percent DECIMAL(5,2),
    rr_ratio_1 DECIMAL(5,2),
    rr_ratio_2 DECIMAL(5,2),
    trade_quality VARCHAR(20),
    
    -- Position sizing
    max_allocation_percent DECIMAL(5,2),
    kelly_fraction DECIMAL(5,4),
    recommended_shares INTEGER,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    valid_until TIMESTAMP WITH TIME ZONE
);

-- Backtesting tables
CREATE TABLE backtest_strategies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    user_id INTEGER REFERENCES users(id),
    strategy_config JSONB NOT NULL, -- Strategy parameters and rules
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE backtest_results (
    id SERIAL PRIMARY KEY,
    strategy_id INTEGER REFERENCES backtest_strategies(id),
    stock_id INTEGER REFERENCES stocks(id),
    
    -- Test parameters
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    initial_capital DECIMAL(15,2) NOT NULL,
    
    -- Performance metrics
    final_capital DECIMAL(15,2) NOT NULL,
    total_return DECIMAL(8,4),
    annualized_return DECIMAL(8,4),
    max_drawdown DECIMAL(8,4),
    sharpe_ratio DECIMAL(8,4),
    sortino_ratio DECIMAL(8,4),
    win_rate DECIMAL(5,2),
    profit_factor DECIMAL(8,4),
    avg_trade_return DECIMAL(8,4),
    
    -- Trade statistics
    total_trades INTEGER,
    winning_trades INTEGER,
    losing_trades INTEGER,
    avg_trade_duration INTEGER, -- in days
    
    -- Risk metrics
    volatility DECIMAL(8,4),
    var_95 DECIMAL(8,4), -- Value at Risk 95%
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    detailed_results JSONB -- Additional metrics and trade-by-trade data
);

-- Portfolio management tables
CREATE TABLE portfolios (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    initial_capital DECIMAL(15,2) NOT NULL,
    current_capital DECIMAL(15,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, name)
);

CREATE TABLE portfolio_positions (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER REFERENCES portfolios(id),
    stock_id INTEGER REFERENCES stocks(id),
    quantity INTEGER NOT NULL,
    avg_cost_price DECIMAL(12,2) NOT NULL,
    current_price DECIMAL(12,2),
    unrealized_pnl DECIMAL(15,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(portfolio_id, stock_id)
);

CREATE TABLE portfolio_transactions (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER REFERENCES portfolios(id),
    stock_id INTEGER REFERENCES stocks(id),
    transaction_type VARCHAR(20) NOT NULL, -- BUY, SELL
    quantity INTEGER NOT NULL,
    price DECIMAL(12,2) NOT NULL,
    brokerage DECIMAL(10,2),
    taxes DECIMAL(10,2),
    total_amount DECIMAL(15,2) NOT NULL,
    transaction_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    notes TEXT
);

-- Alert system tables
CREATE TABLE alert_rules (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    stock_id INTEGER REFERENCES stocks(id),
    rule_name VARCHAR(255) NOT NULL,
    rule_type VARCHAR(50) NOT NULL, -- price, signal, volume, pattern, risk
    conditions JSONB NOT NULL, -- Alert conditions
    is_active BOOLEAN DEFAULT TRUE,
    notification_channels JSONB DEFAULT '[]', -- email, sms, push, webhook
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE alert_notifications (
    id SERIAL PRIMARY KEY,
    alert_rule_id INTEGER REFERENCES alert_rules(id),
    message TEXT NOT NULL,
    severity VARCHAR(20) DEFAULT 'medium', -- low, medium, high, critical
    triggered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    acknowledged_by INTEGER REFERENCES users(id),
    sent_channels JSONB DEFAULT '[]' -- Track which channels were used
);

-- ============================================================================
-- TIMESCALEDB TABLES (Time-Series Data)
-- ============================================================================

-- OHLCV data with smart money annotations
CREATE TABLE ohlcv_data (
    time TIMESTAMP WITH TIME ZONE NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    timeframe VARCHAR(20) NOT NULL,
    open DECIMAL(12,2) NOT NULL,
    high DECIMAL(12,2) NOT NULL,
    low DECIMAL(12,2) NOT NULL,
    close DECIMAL(12,2) NOT NULL,
    volume BIGINT NOT NULL,
    
    -- Smart money annotations
    is_fvg_candle BOOLEAN DEFAULT FALSE,
    is_liquidity_grab BOOLEAN DEFAULT FALSE,
    is_order_block_candle BOOLEAN DEFAULT FALSE,
    structure_break_type VARCHAR(20), -- BOS, CHOCH, NONE
    
    -- Additional metrics
    vwap DECIMAL(12,2),
    typical_price DECIMAL(12,2),
    weighted_close_price DECIMAL(12,2),
    
    PRIMARY KEY (time, symbol, timeframe)
);

-- Convert to TimescaleDB hypertable
SELECT create_hypertable('ohlcv_data', 'time', 'symbol', 4);

-- Technical indicators time-series
CREATE TABLE technical_indicators (
    time TIMESTAMP WITH TIME ZONE NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    timeframe VARCHAR(20) NOT NULL,
    indicator_name VARCHAR(50) NOT NULL,
    indicator_value DECIMAL(15,6) NOT NULL,
    signal VARCHAR(20), -- bullish, bearish, neutral
    confidence DECIMAL(5,2),
    
    PRIMARY KEY (time, symbol, timeframe, indicator_name)
);

SELECT create_hypertable('technical_indicators', 'time', 'symbol', 4);

-- Volume profile time-series
CREATE TABLE volume_profile_ts (
    time TIMESTAMP WITH TIME ZONE NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    timeframe VARCHAR(20) NOT NULL,
    poc DECIMAL(12,2) NOT NULL,
    value_area_high DECIMAL(12,2) NOT NULL,
    value_area_low DECIMAL(12,2) NOT NULL,
    total_volume BIGINT NOT NULL,
    volume_levels JSONB NOT NULL,
    volume_gap BOOLEAN DEFAULT FALSE,
    
    PRIMARY KEY (time, symbol, timeframe)
);

SELECT create_hypertable('volume_profile_ts', 'time', 'symbol', 4);

-- Market data events
CREATE TABLE market_events (
    time TIMESTAMP WITH TIME ZONE NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    event_type VARCHAR(50) NOT NULL, -- fvg_created, fvg_mitigated, structure_break, volume_spike
    event_data JSONB NOT NULL,
    confidence DECIMAL(5,2),
    
    PRIMARY KEY (time, symbol, event_type)
);

SELECT create_hypertable('market_events', 'time', 'symbol', 4);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- PostgreSQL indexes
CREATE INDEX idx_stocks_symbol ON stocks(symbol);
CREATE INDEX idx_stocks_sector ON stocks(sector);
CREATE INDEX idx_stocks_exchange ON stocks(exchange);

CREATE INDEX idx_signals_stock_id ON signals(stock_id);
CREATE INDEX idx_signals_created_at ON signals(created_at);
CREATE INDEX idx_signals_signal_type ON signals(signal_type);
CREATE INDEX idx_signals_source ON signals(source);

CREATE INDEX idx_aggregated_signals_stock_id ON aggregated_signals(stock_id);
CREATE INDEX idx_aggregated_signals_created_at ON aggregated_signals(created_at);

CREATE INDEX idx_watchlists_user_id ON watchlists(user_id);
CREATE INDEX idx_watchlist_stocks_watchlist_id ON watchlist_stocks(watchlist_id);

CREATE INDEX idx_fvg_zones_stock_id ON fvg_zones(stock_id);
CREATE INDEX idx_fvg_zones_timeframe ON fvg_zones(timeframe);
CREATE INDEX idx_fvg_zones_mitigated ON fvg_zones(mitigated);

CREATE INDEX idx_order_blocks_stock_id ON order_blocks(stock_id);
CREATE INDEX idx_order_blocks_block_type ON order_blocks(block_type);

CREATE INDEX idx_market_structure_stock_id ON market_structure(stock_id);
CREATE INDEX idx_market_structure_trend ON market_structure(trend);

CREATE INDEX idx_detected_patterns_stock_id ON detected_patterns(stock_id);
CREATE INDEX idx_detected_patterns_pattern_type ON detected_patterns(pattern_type);

CREATE INDEX idx_fundamental_data_stock_id ON fundamental_data(stock_id);
CREATE INDEX idx_fundamental_data_report_date ON fundamental_data(report_date);

CREATE INDEX idx_risk_metrics_stock_id ON risk_metrics(stock_id);
CREATE INDEX idx_risk_metrics_risk_rating ON risk_metrics(risk_rating);

CREATE INDEX idx_backtest_results_strategy_id ON backtest_results(strategy_id);
CREATE INDEX idx_backtest_results_created_at ON backtest_results(created_at);

CREATE INDEX idx_portfolio_positions_portfolio_id ON portfolio_positions(portfolio_id);
CREATE INDEX idx_portfolio_transactions_portfolio_id ON portfolio_transactions(portfolio_id);

CREATE INDEX idx_alert_rules_user_id ON alert_rules(user_id);
CREATE INDEX idx_alert_rules_stock_id ON alert_rules(stock_id);

CREATE INDEX idx_alert_notifications_alert_rule_id ON alert_notifications(alert_rule_id);
CREATE INDEX idx_alert_notifications_triggered_at ON alert_notifications(triggered_at);

-- TimescaleDB indexes (automatically created on time column)
CREATE INDEX idx_ohlcv_data_symbol_timeframe ON ohlcv_data(symbol, timeframe);
CREATE INDEX idx_technical_indicators_symbol_timeframe ON technical_indicators(symbol, timeframe);
CREATE INDEX idx_volume_profile_ts_symbol_timeframe ON volume_profile_ts(symbol, timeframe);

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Latest signals for all stocks
CREATE VIEW latest_signals AS
SELECT DISTINCT ON (stock_id, source)
    stock_id,
    symbol,
    signal_type,
    source,
    strength,
    confidence,
    timeframe,
    explanation,
    created_at
FROM signals s
JOIN stocks st ON s.stock_id = st.id
WHERE s.is_active = TRUE
    AND (s.expires_at IS NULL OR s.expires_at > NOW())
ORDER BY stock_id, source, created_at DESC;

-- Active FVG zones
CREATE VIEW active_fvg_zones AS
SELECT 
    fvg.id,
    st.symbol,
    fvg.timeframe,
    fvg.zone_type,
    fvg.high_price,
    fvg.low_price,
    fvg.midpoint,
    fvg.strength,
    fvg.created_at
FROM fvg_zones fvg
JOIN stocks st ON fvg.stock_id = st.id
WHERE fvg.mitigated = FALSE
    AND fvg.valid_until > NOW();

-- Recent market structure changes
CREATE VIEW recent_structure_changes AS
SELECT 
    ms.id,
    st.symbol,
    ms.timeframe,
    ms.trend,
    ms.last_bos,
    ms.last_choch,
    ms.created_at
FROM market_structure ms
JOIN stocks st ON ms.stock_id = st.id
WHERE ms.created_at > NOW() - INTERVAL '7 days'
ORDER BY ms.created_at DESC;

-- Portfolio performance summary
CREATE VIEW portfolio_performance AS
SELECT 
    p.id as portfolio_id,
    p.name as portfolio_name,
    p.initial_capital,
    p.current_capital,
    (p.current_capital - p.initial_capital) as total_pnl,
    ((p.current_capital - p.initial_capital) / p.initial_capital * 100) as total_return_percent,
    COUNT(pp.id) as position_count,
    SUM(pp.unrealized_pnl) as total_unrealized_pnl
FROM portfolios p
LEFT JOIN portfolio_positions pp ON p.id = pp.portfolio_id
GROUP BY p.id, p.name, p.initial_capital, p.current_capital;

-- ============================================================================
-- STORED PROCEDURES AND FUNCTIONS
-- ============================================================================

-- Function to calculate portfolio value
CREATE OR REPLACE FUNCTION calculate_portfolio_value(portfolio_id_param INTEGER)
RETURNS DECIMAL(15,2) AS $$
DECLARE
    total_value DECIMAL(15,2);
BEGIN
    SELECT COALESCE(SUM(pp.quantity * pp.current_price), 0)
    INTO total_value
    FROM portfolio_positions pp
    WHERE pp.portfolio_id = portfolio_id_param;
    
    RETURN total_value;
END;
$$ LANGUAGE plpgsql;

-- Function to update portfolio capital
CREATE OR REPLACE FUNCTION update_portfolio_capital(portfolio_id_param INTEGER)
RETURNS VOID AS $$
DECLARE
    current_value DECIMAL(15,2);
BEGIN
    current_value := calculate_portfolio_value(portfolio_id_param);
    
    UPDATE portfolios 
    SET current_capital = current_value,
        updated_at = NOW()
    WHERE id = portfolio_id_param;
END;
$$ LANGUAGE plpgsql;

-- Function to clean up old signals
CREATE OR REPLACE FUNCTION cleanup_old_signals(days_old INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM signals 
    WHERE created_at < NOW() - INTERVAL '1 day' * days_old;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- TRIGGERS FOR AUTOMATIC UPDATES
-- ============================================================================

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to relevant tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_stocks_updated_at BEFORE UPDATE ON stocks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_watchlists_updated_at BEFORE UPDATE ON watchlists
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_fundamental_data_updated_at BEFORE UPDATE ON fundamental_data
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_portfolio_positions_updated_at BEFORE UPDATE ON portfolio_positions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_portfolios_updated_at BEFORE UPDATE ON portfolios
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger to update portfolio capital when positions change
CREATE OR REPLACE FUNCTION update_portfolio_on_position_change()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM update_portfolio_capital(NEW.portfolio_id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_portfolio_after_position_change 
    AFTER INSERT OR UPDATE OR DELETE ON portfolio_positions
    FOR EACH ROW EXECUTE FUNCTION update_portfolio_on_position_change();

-- ============================================================================
-- TIMESCALEDB CONTINUOUS AGGREGATES
-- ============================================================================

-- Daily OHLCV aggregates
CREATE MATERIALIZED VIEW daily_ohlcv_summary
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 day', time) AS day,
    symbol,
    FIRST(open, time) AS open,
    MAX(high) AS high,
    MIN(low) AS low,
    LAST(close, time) AS close,
    SUM(volume) AS volume,
    AVG(volume) AS avg_volume
FROM ohlcv_data
WHERE timeframe = 'daily'
GROUP BY day, symbol;

-- Add refresh policy
SELECT add_continuous_aggregate_policy('daily_ohlcv_summary', 
    start_offset => INTERVAL '1 month',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour');

-- Weekly technical indicators summary
CREATE MATERIALIZED VIEW weekly_indicators_summary
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 week', time) AS week,
    symbol,
    indicator_name,
    AVG(indicator_value) as avg_value,
    MIN(indicator_value) as min_value,
    MAX(indicator_value) as max_value,
    STDDEV(indicator_value) as stddev_value
FROM technical_indicators
WHERE timeframe = 'daily'
GROUP BY week, symbol, indicator_name;

SELECT add_continuous_aggregate_policy('weekly_indicators_summary',
    start_offset => INTERVAL '3 months',
    end_offset => INTERVAL '1 day',
    schedule_interval => INTERVAL '1 day');

-- ============================================================================
-- SAMPLE DATA INSERTION (for development)
-- ============================================================================

-- Insert sample stocks
INSERT INTO stocks (symbol, name, sector, industry, exchange, market_cap_category) VALUES
('RELIANCE', 'Reliance Industries Ltd', 'Energy', 'Oil & Gas', 'NSE', 'large_cap'),
('TCS', 'Tata Consultancy Services', 'Technology', 'IT Services', 'NSE', 'large_cap'),
('HDFCBANK', 'HDFC Bank Ltd', 'Banking', 'Private Bank', 'NSE', 'large_cap'),
('INFY', 'Infosys Ltd', 'Technology', 'IT Services', 'NSE', 'large_cap'),
('ICICIBANK', 'ICICI Bank Ltd', 'Banking', 'Private Bank', 'NSE', 'large_cap');

-- Insert sample user
INSERT INTO users (email, password_hash, role, first_name, last_name) VALUES
('admin@tradingframework.com', 'hashed_password', 'admin', 'Admin', 'User');

-- Create indexes for better query performance on JSONB columns
CREATE INDEX idx_signals_raw_data_gin ON signals USING GIN (raw_data);
CREATE INDEX idx_fundamental_data_metadata_gin ON fundamental_data USING GIN (metadata);
CREATE INDEX idx_stocks_metadata_gin ON stocks USING GIN (metadata);

-- Grant permissions (adjust as needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO trading_framework_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO trading_framework_user;
