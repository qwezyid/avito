#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.avito_token_manager import token_manager

if __name__ == "__main__":
    print("Starting Avito token service...")
    token_manager.start_scheduler()
    
    try:
        while True:
            import time
            time.sleep(60)
    except KeyboardInterrupt:
        print("Stopping token service...")
        token_manager.stop_scheduler()
