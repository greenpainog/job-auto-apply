#!/usr/bin/env python3
"""
Test the auto-apply setup
"""

import os
import json
from datetime import datetime

def test_setup():
    print("🧪 Testing Auto-Apply Setup...")
    print("=" * 50)
    
    # Check config file
    if os.path.exists('auto_apply_config.json'):
        print("✅ Config file found")
        with open('auto_apply_config.json', 'r') as f:
            config = json.load(f)
            print(f"   Email: {config.get('email', 'Not set')}")
            print(f"   Keywords: {config.get('keywords', [])}")
    else:
        print("❌ Config file not found - create auto_apply_config.json")
    
    # Check auto_applier module
    try:
        from auto_applier import JobAutoApplier
        print("✅ auto_applier module works")
    except ImportError as e:
        print(f"❌ auto_applier module error: {e}")
    
    # Check job_scraper module
    try:
        from job_scraper import JobScraper
        print("✅ job_scraper module works")
    except ImportError as e:
        print(f"❌ job_scraper module error: {e}")
    
    # Check data directories
    if not os.path.exists('data'):
        os.makedirs('data')
    print("✅ Data directory ready")
    
    print("\n" + "=" * 50)
    print("Setup test complete!")

if __name__ == "__main__":
    test_setup()