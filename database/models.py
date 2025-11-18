"""
Database Models
PostgreSQL schema for predictions, learning data, and stock data
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

Base = declarative_base()


class Prediction(Base):
    """
    Store all predictions for learning
    """
    __tablename__ = 'predictions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(20), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Price data
    entry_price = Column(Float, nullable=False)
    current_price = Column(Float)
    
    # Prediction
    recommendation = Column(String(20), nullable=False)  # BUY, SELL, HOLD
    composite_score = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    
    # Agent outputs (stored as JSON)
    agent_scores = Column(JSONB)
    agent_signals = Column(JSONB)
    agent_reasoning = Column(JSONB)
    
    # Features used
    technical_features = Column(JSONB)
    fundamental_features = Column(JSONB)
    
    # Multimodal data
    earnings_sentiment = Column(Float)
    report_quality = Column(Float)
    chart_patterns = Column(JSONB)
    
    # Evaluation
    evaluation_date = Column(DateTime, nullable=False)
    evaluated = Column(Boolean, default=False, index=True)
    evaluation_timestamp = Column(DateTime)
    
    # Outcome
    actual_return = Column(Float)
    predicted_return = Column(Float)
    error_margin = Column(Float)
    is_correct = Column(Boolean)
    
    # Agent evaluation
    agent_evaluation = Column(JSONB)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes for fast queries
    __table_args__ = (
        Index('idx_ticker_timestamp', 'ticker', 'timestamp'),
        Index('idx_evaluated', 'evaluated', 'evaluation_date'),
        Index('idx_ticker_evaluated', 'ticker', 'evaluated'),
    )


class AgentAccuracy(Base):
    """
    Track agent accuracy over time
    """
    __tablename__ = 'agent_accuracy'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_name = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Accuracy metrics
    total_predictions = Column(Integer, default=0)
    correct_predictions = Column(Integer, default=0)
    accuracy_rate = Column(Float, default=0.0)
    
    # Performance by category
    accuracy_by_sector = Column(JSONB)
    accuracy_by_market_regime = Column(JSONB)
    
    # Weight
    current_weight = Column(Float, nullable=False)
    previous_weight = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_agent_timestamp', 'agent_name', 'timestamp'),
    )


class FeatureImportance(Base):
    """
    Track which features are most predictive
    """
    __tablename__ = 'feature_importance'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    feature_name = Column(String(100), nullable=False, index=True)
    feature_category = Column(String(50))  # technical, fundamental, etc.
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Importance metrics
    total_uses = Column(Integer, default=0)
    correct_predictions = Column(Integer, default=0)
    accuracy_rate = Column(Float, default=0.0)
    
    # Statistical measures
    correlation_with_outcome = Column(Float)
    information_gain = Column(Float)
    
    # Current weight
    current_weight = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class StockData(Base):
    """
    Cache stock data to reduce API calls
    """
    __tablename__ = 'stock_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(20), nullable=False, index=True)
    data_type = Column(String(50), nullable=False)  # price, fundamental, technical
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Data source
    source = Column(String(50))  # yahoo, tradingview, nse, bse
    
    # Actual data (stored as JSON)
    data = Column(JSONB, nullable=False)
    
    # Cache metadata
    expires_at = Column(DateTime, nullable=False)
    is_valid = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_ticker_type_timestamp', 'ticker', 'data_type', 'timestamp'),
        Index('idx_expires', 'expires_at', 'is_valid'),
    )


class LearningIteration(Base):
    """
    Track learning iterations and improvements
    """
    __tablename__ = 'learning_iterations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    iteration_number = Column(Integer, nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Metrics
    total_predictions = Column(Integer)
    evaluated_predictions = Column(Integer)
    overall_accuracy = Column(Float)
    
    # Agent weights
    agent_weights = Column(JSONB)
    
    # Feature importance (top 20)
    top_features = Column(JSONB)
    
    # Performance by category
    accuracy_by_sector = Column(JSONB)
    accuracy_by_market_regime = Column(JSONB)
    
    # Improvements
    accuracy_improvement = Column(Float)
    best_performing_agent = Column(String(50))
    worst_performing_agent = Column(String(50))
    
    # Notes
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class PatternAccuracy(Base):
    """
    Track accuracy of chart patterns
    """
    __tablename__ = 'pattern_accuracy'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    pattern_name = Column(String(100), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Detection
    total_detected = Column(Integer, default=0)
    successful_predictions = Column(Integer, default=0)
    accuracy_rate = Column(Float, default=0.0)
    
    # Performance metrics
    avg_return_when_correct = Column(Float)
    avg_return_when_wrong = Column(Float)
    
    # Reliability
    reliability_score = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EarningsCallData(Base):
    """
    Store earnings call analysis
    """
    __tablename__ = 'earnings_calls'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(20), nullable=False, index=True)
    call_date = Column(DateTime, nullable=False, index=True)
    
    # Analysis
    sentiment = Column(Float)
    management_tone = Column(String(50))
    confidence = Column(Float)
    
    # Content
    key_points = Column(JSONB)
    guidance = Column(String(50))
    concerns = Column(JSONB)
    opportunities = Column(JSONB)
    
    # Transcript
    transcript_url = Column(String(500))
    transcript_excerpt = Column(Text)
    
    # Evaluation
    prediction_accuracy = Column(Float)
    evaluated = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class FinancialReportData(Base):
    """
    Store financial report analysis
    """
    __tablename__ = 'financial_reports'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(20), nullable=False, index=True)
    report_date = Column(DateTime, nullable=False, index=True)
    report_type = Column(String(50))  # annual, quarterly
    
    # Metrics
    metrics = Column(JSONB)
    quality_score = Column(Float)
    
    # Analysis
    insights = Column(JSONB)
    red_flags = Column(JSONB)
    growth_initiatives = Column(JSONB)
    
    # File
    report_url = Column(String(500))
    
    created_at = Column(DateTime, default=datetime.utcnow)


if __name__ == "__main__":
    print("Database models defined:")
    print("  - Prediction")
    print("  - AgentAccuracy")
    print("  - FeatureImportance")
    print("  - StockData")
    print("  - LearningIteration")
    print("  - PatternAccuracy")
    print("  - EarningsCallData")
    print("  - FinancialReportData")
