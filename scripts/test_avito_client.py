#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.avito_client import avito_client

def test_avito_client():
    print("Testing Avito client...")
    
    token = avito_client.get_active_token()
    if token:
        print(f"✅ Active token found: {token[:20]}...")
        return True
    else:
        print("❌ No active token")
        return False

if __name__ == "__main__":
    test_avito_client()
