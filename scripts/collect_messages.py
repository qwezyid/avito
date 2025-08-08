#!/usr/bin/env python3

import sys
import os
import time
import psycopg2
import psycopg2.extras
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.avito_client import avito_client

class SimpleMessageCollector:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.db_config = {
            'host': "89.169.45.152",
            'database': "Avito",
            'user': "Tim",
            'password': "AVITOPassw0rd"
        }
        
    def collect_messages(self):
        chats = avito_client.get_chats(self.user_id, limit=10)
        if not chats:
            print("No chats found")
            return
        
        new_messages = 0
        
        for chat in chats:
            chat_id = chat['id']
            print(f"\nProcessing chat: {chat_id}")
            
            # Простое сохранение чата без внешних ключей
            self.save_chat_simple(chat)
            
            messages = avito_client.get_messages(self.user_id, chat_id, limit=10)
            if not messages:
                continue
                
            for message in messages:
                if self.save_message_simple(chat_id, message):
                    new_messages += 1
                    direction_icon = "➡️" if message['direction'] == 'out' else "⬅️"
                    text = message.get('content', {}).get('text', 'No text')[:30]
                    print(f"  {direction_icon} {text}...")
        
        print(f"\n✅ Collected {new_messages} new messages")
    
    def save_chat_simple(self, chat):
        try:
            conn = psycopg2.connect(**self.db_config)
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO avito_chats 
                    (chat_id, created, updated, chat_status, ai_stage)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (chat_id) DO UPDATE SET
                        updated = EXCLUDED.updated
                """, (
                    chat['id'],
                    chat['created'],
                    chat['updated'],
                    'active',
                    'greeting'
                ))
                conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving chat: {e}")
            return False
    
    def save_message_simple(self, chat_id, message):
        try:
            conn = psycopg2.connect(**self.db_config)
            with conn.cursor() as cursor:
                # Проверяем существование
                cursor.execute("SELECT 1 FROM avito_messages WHERE message_id = %s", (message['id'],))
                if cursor.fetchone():
                    conn.close()
                    return False
                
                cursor.execute("""
                    INSERT INTO avito_messages 
                    (message_id, chat_id, author_id, created, direction, message_type, 
                     content_text, ai_processed)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    message['id'],
                    chat_id,
                    message.get('author_id', 0),
                    message['created'],
                    message['direction'],
                    message.get('type', 'text'),
                    message.get('content', {}).get('text', ''),
                    False
                ))
                
                conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error saving message: {e}")
            return False

if __name__ == "__main__":
    collector = SimpleMessageCollector(user_id=414329950)
    print("Collecting messages...")
    collector.collect_messages()
