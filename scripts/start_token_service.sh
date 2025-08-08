#!/bin/bash
cd /root/avito-ai-assistant
source venv/bin/activate
nohup python scripts/run_token_service.py > logs/token_service.log 2>&1 &
echo $! > /var/run/avito_token_service.pid
echo "Token service started with PID $(cat /var/run/avito_token_service.pid)"
