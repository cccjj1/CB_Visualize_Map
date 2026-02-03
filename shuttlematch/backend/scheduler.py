#!/usr/bin/env python3
"""
Background Scheduler for Shuttle Matching Algorithm
Runs matching algorithm periodically based on mode:
- test: every 30 seconds
- prod: daily at 00:00
"""
import schedule
import time
import subprocess
import os
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Determine mode
SHUTTLE_MODE = os.getenv('SHUTTLE_MODE', 'test')

def run_matching_algorithm():
    """Execute the matching algorithm"""
    logger.info("🧬 Starting matching algorithm...")
    
    try:
        # Get the directory of this script
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        algorithm_script = os.path.join(backend_dir, 'matching_algorithm.py')
        
        # Run algorithm using subprocess
        result = subprocess.run(
            ['python3', algorithm_script],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        if result.returncode == 0:
            logger.info("✅ Algorithm completed successfully")
            logger.debug(f"Output: {result.stdout}")
        else:
            logger.error(f"❌ Algorithm failed with code {result.returncode}")
            logger.error(f"Error: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        logger.error("❌ Algorithm execution timeout")
    except Exception as e:
        logger.error(f"❌ Error running algorithm: {str(e)}")

def schedule_jobs():
    """Schedule matching algorithm based on mode"""
    
    if SHUTTLE_MODE == 'test':
        # Test mode: run every 30 seconds
        logger.info("📅 Mode: TEST (every 30 seconds)")
        schedule.every(30).seconds.do(run_matching_algorithm)
    else:
        # Production mode: run daily at 00:00
        logger.info("📅 Mode: PRODUCTION (daily at 00:00)")
        schedule.every().day.at("00:00").do(run_matching_algorithm)

def main():
    """Main scheduler loop"""
    logger.info("="*60)
    logger.info("🚌 Campus Shuttle Matching Scheduler Started")
    logger.info(f"Mode: {SHUTTLE_MODE.upper()}")
    logger.info("="*60)
    
    # Schedule jobs
    schedule_jobs()
    
    # Keep scheduler running
    logger.info("⏳ Scheduler waiting for next job...")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n🛑 Scheduler stopped by user")
