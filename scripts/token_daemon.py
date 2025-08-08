#!/usr/bin/env python3

import sys
import os
import signal
import daemon
import lockfile
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.avito_token_manager import token_manager

def run_token_service():
    token_manager.start_scheduler()
    try:
        while token_manager.running:
            import time
            time.sleep(60)
    except Exception as e:
        print(f"Service error: {e}")

def signal_handler(signum, frame):
    token_manager.stop_scheduler()
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    with daemon.DaemonContext(
        working_directory='/root/avito-ai-assistant',
        pidfile=lockfile.FileLock('/var/run/avito_token_service.pid')
    ):
        run_token_service()
