#!/usr/bin/env python3

import sys
import os
import time
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.avito_client import avito_client
from src.core.rabbitmq_manager import rabbitmq_manager

def monitor_new_messages():
    user_id = 414329950  # Replace with your real user_id
    processed_messages = set()
    
    print(f"Monitoring messages for user {user_id}...")
    print("Send a message in Avito chat and watch for new messages here")
    
    while True:
        try:
            # Получаем чаты
            chats = avito_client.get_chats(user_id, limit=10)
            if not chats:
                print("No chats found")
                time.sleep(10)
                continue
            
            for chat in chats:
                chat_id = chat.get('id')
                
                # Получаем последние сообщения
                messages = avito_client.get_messages(user_id, chat_id, limit=5)
                if not messages:
                    continue
                
                for message in messages:
                    message_id = message.get('id')
                    direction = message.get('direction')
                    
                    # Проверяем новые входящие сообщения
                    if (message_id not in processed_messages and 
                        direction == 'in' and 
                        message.get('content', {}).get('text')):
                        
                        print(f"\n🆕 NEW MESSAGE in chat {chat_id}:")
                        print(f"   ID: {message_id}")
                        print(f"   Author: {message.get('author_id')}")
                        print(f"   Text: {message.get('content', {}).get('text')}")
                        print(f"   Time: {message.get('created')}")
                        
                        # Отправляем в очередь для обработки
                        message_data = {
                            'chat_id': chat_id,
                            'message_id': message_id,
                            'author_id': message.get('author_id'),
                            'text': message.get('content', {}).get('text'),
                            'created': message.get('created'),
                            'user_id': user_id
                        }
                        
                        success = rabbitmq_manager.send_message('incoming_messages', message_data)
                        if success:
                            print("   ✅ Queued for processing")
                            processed_messages.add(message_id)
                        else:
                            print("   ❌ Failed to queue")
            
            time.sleep(15)  # Проверяем каждые 15 секунд
            
        except KeyboardInterrupt:
            print("\nStopping monitor...")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    monitor_new_messages()
