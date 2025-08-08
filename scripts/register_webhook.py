#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.avito_client import avito_client

def register_webhook():
    webhook_url = "http://exampro.dad/avito/webhook"  # Замени на свой домен
    
    print(f"Registering webhook: {webhook_url}")
    
    response = avito_client.make_request(
        'POST', 
        '/messenger/v3/webhook',
        json={'url': webhook_url}
    )
    
    if response and response.status_code == 200:
        print("✅ Webhook registered successfully")
        print(f"Response: {response.json()}")
    else:
        print(f"❌ Registration failed: {response.status_code if response else 'No response'}")
        if response:
            print(f"Error: {response.text}")

if __name__ == "__main__":
    register_webhook()
