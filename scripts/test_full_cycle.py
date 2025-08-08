#!/usr/bin/env python3

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.rabbitmq_manager import rabbitmq_manager
from src.services.avito_client import avito_client

def test_message_cycle():
    print("Testing full message cycle...")
    
    # Тест 1: Проверяем токен
    token = avito_client.get_active_token()
    if not token:
        print("❌ No active token")
        return False
    print("✅ Token available")
    
    # Тест 2: Симулируем входящее сообщение
    test_message = {
        'chat_id': 'test_chat_123',
        'message_id': 'test_msg_456',
        'author_id': 789,
        'text': 'Привет! Нужна перевозка груза',
        'created': int(time.time()),
        'direction': 'in',
        'type': 'text',
        'user_id': 414329950
    }
    
    success = rabbitmq_manager.send_message('incoming_messages', test_message)
    if success:
        print("✅ Test message queued")
    else:
        print("❌ Failed to queue message")
        return False
    
    # Тест 3: Проверяем очереди
    for queue_type in ['incoming_messages', 'ai_processing', 'outgoing_messages']:
        info = rabbitmq_manager.get_queue_info(queue_type)
        if info:
            print(f"📊 {queue_type}: {info['message_count']} messages")
        else:
            print(f"❌ Cannot get {queue_type} info")
    
    print("🎉 Full cycle test completed")
    return True

if __name__ == "__main__":
    test_message_cycle()
