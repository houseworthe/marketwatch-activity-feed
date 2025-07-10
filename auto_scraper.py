#!/usr/bin/env python3
"""
Automated scraper that runs every 5 minutes to update competition data.
"""

import time
import subprocess
import sys
import os
from datetime import datetime

def run_scrapers():
    """Run both leaderboard and competition scrapers."""
    print(f"\n{'='*60}")
    print(f"Starting scraper run at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    try:
        # Run leaderboard scraper first to get latest standings
        print("Running leaderboard scraper...")
        result1 = subprocess.run([sys.executable, 'leaderboard_scraper.py'], 
                                capture_output=True, text=True, timeout=120)
        
        if result1.returncode != 0:
            print(f"Leaderboard scraper failed: {result1.stderr}")
            return False
        
        print("✓ Leaderboard scraper completed successfully")
        
        # Run competition scraper to get detailed data
        print("Running competition scraper...")
        result2 = subprocess.run([sys.executable, 'competition_scraper.py'], 
                                capture_output=True, text=True, timeout=300)
        
        if result2.returncode != 0:
            print(f"Competition scraper failed: {result2.stderr}")
            return False
        
        print("✓ Competition scraper completed successfully")
        
        # Copy fresh data to frontend
        print("Copying data to frontend...")
        result3 = subprocess.run(['cp', 'competition_data.json', 'frontend/public/'], 
                                capture_output=True, text=True)
        
        if result3.returncode != 0:
            print(f"Failed to copy data: {result3.stderr}")
            return False
        
        print("✓ Data copied to frontend successfully")
        print(f"Scraper run completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return True
        
    except subprocess.TimeoutExpired:
        print("Scraper timed out")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def main():
    """Main loop - run scrapers every 5 minutes."""
    print("Starting automated scraper - will run every 5 minutes")
    print("Press Ctrl+C to stop")
    
    # Run immediately on start
    run_scrapers()
    
    try:
        while True:
            print(f"\nWaiting 5 minutes until next run...")
            time.sleep(300)  # 5 minutes = 300 seconds
            run_scrapers()
            
    except KeyboardInterrupt:
        print("\nStopping automated scraper...")
        sys.exit(0)

if __name__ == "__main__":
    main()