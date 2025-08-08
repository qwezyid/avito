#!/bin/bash
if [ -f /var/run/avito_token_service.pid ]; then
    PID=$(cat /var/run/avito_token_service.pid)
    kill $PID
    rm /var/run/avito_token_service.pid
    echo "Token service stopped"
else
    echo "Token service not running"
fi
