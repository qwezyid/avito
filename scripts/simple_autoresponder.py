#!/usr/bin/env python3

import sys
import os
import time
import psycopg2
import psycopg2.extras
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.avito_client import avito_client

class AutoResponder:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.db_config = {
            'host': "89.169.45.152",
            'database': "Avito",
            'user': "Tim",
            'password': "AVITOPassw0rd"
        }
    
    def run(self):
        print("Auto-responder started. Send message in Avito to test...")
        
        while True:
            try:
                messages = self.get_new_messages()
                
                for message in messages:
                    chat_id = message['chat_id']
                    text = message['content_text']
                    
                    print(f"\n📨 New: {text[:50]}...")
                    
                    response = self.generate_response(text)
                    
                    result = avito_client.send_message(self.user_id, chat_id, response)
                    
                    if result:
                        print(f"✅ Sent: {response[:50]}...")
                        self.mark_processed(message['message_id'])
                    else:
                        print("❌ Send failed")
                
                time.sleep(15)
                
            except KeyboardInterrupt:
                print("\nStopping...")
                break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(5)
    
    def get_new_messages(self):
        try:
            conn = psycopg2.connect(**self.db_config, cursor_factory=psycopg2.extras.RealDictCursor)
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM simple_messages 
                    WHERE direction = 'in' 
                      AND ai_processed = FALSE 
                      AND content_text IS NOT NULL
                      AND content_text != ''
                    ORDER BY created ASC
                    LIMIT 3
                """)
                messages = cursor.fetchall()
            conn.close()
            return messages
        except Exception as e:
            print(f"DB error: {e}")
            return []
    
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
        else:
            return "Спасибо за сообщение! Чем могу помочь с организацией перевозки?"

if __name__ == "__main__":
    responder = AutoResponder(user_id=123456)
    responder.run()
