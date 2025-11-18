#!/usr/bin/env python3
"""
Database Setup Script
Initialize PostgreSQL database and create tables
"""

import os
import sys
from database import init_db, close_db, get_db, Prediction


def setup_database():
    """
    Setup database and create all tables
    """
    print("\n🗄️  DATABASE SETUP")
    print("="*60)
    
    # Check if DATABASE_URL is set
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("\n⚠️  DATABASE_URL not set in environment")
        print("\nOptions:")
        print("  1. Set DATABASE_URL in .env file:")
        print("     DATABASE_URL=postgresql://user:password@localhost/trading_framework")
        print("\n  2. Use default (PostgreSQL on localhost):")
        print("     DATABASE_URL=postgresql://localhost/trading_framework")
        
        use_default = input("\nUse default? (y/n): ").lower()
        
        if use_default == 'y':
            database_url = 'postgresql://localhost/trading_framework'
            print(f"\nUsing: {database_url}")
        else:
            database_url = input("Enter DATABASE_URL: ")
    
    print(f"\n📍 Database URL: {database_url}")
    
    try:
        # Initialize database
        print("\n1. Initializing database connection...")
        init_db(database_url)
        print("   ✅ Connected successfully")
        
        # Create tables
        print("\n2. Creating tables...")
        print("   - predictions")
        print("   - agent_accuracy")
        print("   - feature_importance")
        print("   - stock_data")
        print("   - learning_iterations")
        print("   - pattern_accuracy")
        print("   - earnings_calls")
        print("   - financial_reports")
        print("   ✅ All tables created")
        
        # Test database
        print("\n3. Testing database...")
        with get_db() as session:
            count = session.query(Prediction).count()
            print(f"   ✅ Database working (predictions: {count})")
        
        print("\n" + "="*60)
        print("✅ DATABASE SETUP COMPLETE!")
        print("="*60)
        
        print("\nNext steps:")
        print("  1. Run predictions: python3 analyze_with_learning.py KPIGREEN")
        print("  2. Start scheduler: python3 automation/scheduler.py --daemon")
        
    except Exception as e:
        print(f"\n❌ Database setup failed: {e}")
        print("\nTroubleshooting:")
        print("  1. Make sure PostgreSQL is installed and running")
        print("  2. Create database: createdb trading_framework")
        print("  3. Check DATABASE_URL is correct")
        sys.exit(1)
    
    finally:
        close_db()


if __name__ == "__main__":
    setup_database()
