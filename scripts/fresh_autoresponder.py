#!/usr/bin/env python3

import sys
import os
import time
import psycopg2
import psycopg2.extras
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.avito_client import avito_client

class FreshAutoResponder:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.db_config = {
            'host': "89.169.45.152",
            'database': "Avito",
            'user': "Tim",
            'password': "AVITOPassw0rd"
        }
        self.last_check_time = int(time.time())
        print(f"Starting fresh responder. Current timestamp: {self.last_check_time}")
    
    def run(self):
        print("Fresh auto-responder started (only messages from last 15 minutes)")
        print("Send a message in Avito to test...")
        
        while True:
            try:
                # Собираем только новые сообщения
                self.collect_fresh_messages()
                
                # Обрабатываем непрочитанные
                messages = self.get_fresh_unprocessed_messages()
                
                for message in messages:
                    chat_id = message['chat_id']
                    text = message['content_text']
                    message_time = message['created']
                    
                    # Проверяем что сообщение свежее (последние 15 минут)
                    current_time = int(time.time())
                    if current_time - message_time > 900:  # 15 минут
                        print(f"⏰ Skipping old message: {text[:30]}...")
                        self.mark_processed(message['message_id'])
                        continue
                    
                    print(f"\n📨 Fresh message: {text[:50]}...")
                    print(f"   Time: {message_time}, Age: {current_time - message_time}s")
                    
                    response = self.generate_response(text)
                    
                    result = avito_client.send_message(self.user_id, chat_id, response)
                    
                    if result:
                        print(f"✅ Sent: {response[:50]}...")
                        self.mark_processed(message['message_id'])
                    else:
                        print("❌ Send failed")
                
                time.sleep(30)  # Проверяем каждые 30 секунд
                
            except KeyboardInterrupt:
                print("\nStopping...")
                break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(10)
    
    def collect_fresh_messages(self):
        """Собираем только свежие сообщения"""
        try:
            chats = avito_client.get_chats(self.user_id, limit=20)
            if not chats:
                return
            
            current_time = int(time.time())
            new_count = 0
            
            for chat in chats:
                chat_id = chat['id']
                
                # Проверяем только обновленные недавно чаты
                if current_time - chat['updated'] > 1800:  # 30 минут
                    continue
                
                self.save_chat(chat)
                
                messages = avito_client.get_messages(self.user_id, chat_id, limit=5)
                if not messages:
                    continue
                
                for message in messages:
                    # Сохраняем только свежие сообщения
                    if current_time - message['created'] <= 900:  # 15 минут
                        if self.save_message(chat_id, message):
                            new_count += 1
                            direction = "➡️" if message['direction'] == 'out' else "⬅️"
                            text = message.get('content', {}).get('text', '')[:20]
                            age = current_time - message['created']
                            print(f"  {direction} {text}... (age: {age}s)")
            
            if new_count > 0:
                print(f"🔄 Collected {new_count} fresh messages")
                
        except Exception as e:
            print(f"Collection error: {e}")
    
    def get_fresh_unprocessed_messages(self):
        """Получаем только свежие необработанные сообщения"""
        try:
            conn = psycopg2.connect(**self.db_config, cursor_factory=psycopg2.extras.RealDictCursor)
            with conn.cursor() as cursor:
                current_time = int(time.time())
                fifteen_minutes_ago = current_time - 900
                
                cursor.execute("""
                    SELECT * FROM simple_messages 
                    WHERE direction = 'in' 
                      AND ai_processed = FALSE 
                      AND content_text IS NOT NULL
                      AND content_text != ''
                      AND created > %s
                    ORDER BY created DESC
                    LIMIT 5
                """, (fifteen_minutes_ago,))
                
                messages = cursor.fetchall()
            conn.close()
            return messages
        except Exception as e:
            print(f"DB error: {e}")
            return []
    
    def save_chat(self, chat):
        try:
            conn = psycopg2.connect(**self.db_config)
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO simple_chats (chat_id, created, updated)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (chat_id) DO UPDATE SET updated = EXCLUDED.updated
                """, (chat['id'], chat['created'], chat['updated']))
                conn.commit()
            conn.close()
        except Exception as e:
            print(f"Chat save error: {e}")
    
    def save_message(self, chat_id, message):
        try:
            conn = psycopg2.connect(**self.db_config)
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1 FROM simple_messages WHERE message_id = %s", (message['id'],))
                if cursor.fetchone():
                    conn.close()
                    return False
                
                cursor.execute("""
                    INSERT INTO simple_messages 
                    (message_id, chat_id, author_id, created, direction, message_type, content_text)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    message['id'],
                    chat_id,
                    message.get('author_id', 0),
                    message['created'],
                    message['direction'],
                    message.get('type', 'text'),
                    message.get('content', {}).get('text', '')
                ))
                
                conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Message save error: {e}")
            return False
    
    def mark_processed(self, message_id):
        try:
            conn = psycopg2.connect(**self.db_config)
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE simple_messages 
                    SET ai_processed = TRUE, processed_at = NOW()
                    WHERE message_id = %s
                """, (message_id,))
                conn.commit()
            conn.close()
        except Exception as e:
            print(f"Mark error: {e}")
    
    def generate_response(self, text):
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['привет', 'здравствуйте', 'добрый']):
            return "Добро пожаловать! Помогу организовать перевозку. Откуда и куда нужно везти груз?"
        elif any(word in text_lower for word in ['из', 'от', 'до', 'в', 'маршрут']):
            return "Понял маршрут. Расскажите о грузе - что везем, какой вес и габариты?"
        elif any(word in text_lower for word in ['груз', 'кг', 'тонн', 'мебель']):
            return "Отлично! Рассчитываю стоимость перевозки. Скоро предоставлю точную цену."
        elif any(word in text_lower for word in ['цена', 'стоимость', 'сколько']):
            return "Стоимость составляет примерно 15 000 рублей. Точную цену уточнит менеджер."
        else:
            return "Спасибо за сообщение! Чем могу помочь с организацией перевозки?"

if __name__ == "__main__":
    responder = FreshAutoResponder(user_id=414329950)
    responder.run()
