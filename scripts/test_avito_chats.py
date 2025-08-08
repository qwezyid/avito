#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.avito_client import avito_client
import json

def test_get_chats():
    print("Testing Avito chats retrieval...")
    
    user_id = 414329950

    chats = avito_client.get_chats(user_id, limit=10)
    
    if chats is None:
        print("? Failed to get chats")
        return False
    
    print(f"? Found {len(chats)} chats")
    
    for i, chat in enumerate(chats[:3]):
        print(f"\nChat {i+1}:")
        print(f"  ID: {chat.get('id')}")
        print(f"  Created: {chat.get('created')}")
        print(f"  Updated: {chat.get('updated')}")
        
        chat_id = chat.get('id')
        if chat_id:
            messages = avito_client.get_messages(user_id, chat_id, limit=3)
            if messages and isinstance(messages, list):
                print(f"  Messages: {len(messages)}")
                for msg in messages[:2]:
                    direction = "??" if msg.get('direction') == 'out' else "??"
                    content = msg.get('content', {})
                    text = content.get('text', 'No text') if isinstance(content, dict) else 'No text'
                    print(f"    {direction} {str(text)[:50]}...")
            else:
                print("  No messages or invalid format")
    
    return True

if __name__ == "__main__":
    test_get_chats()