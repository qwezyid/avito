import time
import threading
import psycopg2
import psycopg2.extras
import logging
from typing import List, Dict, Optional

logger = logging.getLogger('message_accumulator')

class MessageAccumulator:
    def __init__(self):
        self.db_config = {
            'host': "89.169.45.152",
            'database': "Avito",
            'user': "Tim",
            'password': "AVITOPassw0rd"
        }
        self.active_chats = {}
        self.accumulation_timeout = 30
        
    def add_message(self, chat_id: str):
        current_time = time.time()
        
        if chat_id in self.active_chats:
            self.active_chats[chat_id]['timer'].cancel()
        
        self.active_chats[chat_id] = {
            'last_activity': current_time,
            'timer': None
        }
        
        timer = threading.Timer(self.accumulation_timeout, self.process_accumulated_messages, args=[chat_id])
        self.active_chats[chat_id]['timer'] = timer
        timer.start()
        
        logger.info(f"Message accumulation started for chat {chat_id}")
    
    def process_accumulated_messages(self, chat_id: str):
        try:
            logger.info(f"Processing accumulated messages for chat {chat_id}")
            
            messages = self.get_chat_unprocessed_messages(chat_id)
            
            if messages:
                history = self.get_chat_history(chat_id, limit=10)
                context = self.build_context(messages, history)
                self.send_to_ai_processing(chat_id, context)
                self.mark_messages_queued(messages)
            
            if chat_id in self.active_chats:
                del self.active_chats[chat_id]
                
        except Exception as e:
            logger.error(f"Error processing accumulated messages: {e}")
    
    def get_chat_unprocessed_messages(self, chat_id: str) -> List[Dict]:
        try:
            conn = psycopg2.connect(**self.db_config, cursor_factory=psycopg2.extras.RealDictCursor)
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM simple_messages 
                    WHERE chat_id = %s 
                      AND direction = 'in' 
                      AND ai_processed = FALSE
                      AND content_text IS NOT NULL
                      AND content_text != ''
                    ORDER BY created ASC
                """, (chat_id,))
                messages = cursor.fetchall()
            conn.close()
            return messages
        except Exception as e:
            logger.error(f"Error getting unprocessed messages: {e}")
            return []
    
    def get_chat_history(self, chat_id: str, limit: int = 10) -> List[Dict]:
        try:
            conn = psycopg2.connect(**self.db_config, cursor_factory=psycopg2.extras.RealDictCursor)
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT content_text, direction, created
                    FROM simple_messages 
                    WHERE chat_id = %s 
                      AND content_text IS NOT NULL
                      AND content_text != ''
                    ORDER BY created DESC
                    LIMIT %s
                """, (chat_id, limit))
                history = cursor.fetchall()
            conn.close()
            return list(reversed(history))
        except Exception as e:
            logger.error(f"Error getting chat history: {e}")
            return []
    
    def build_context(self, new_messages: List[Dict], history: List[Dict]) -> Dict:
        new_messages_text = []
        for msg in new_messages:
            new_messages_text.append(msg['content_text'])
        
        combined_new_text = " ".join(new_messages_text)
        
        history_context = []
        for msg in history:
            role = "assistant" if msg['direction'] == 'out' else "user"
            history_context.append({
                "role": role,
                "content": msg['content_text']
            })
        
        return {
            'new_messages': combined_new_text,
            'history': history_context,
            'message_count': len(new_messages)
        }
    
    def send_to_ai_processing(self, chat_id: str, context: Dict):
        from .ai_decision_engine import ai_decision_engine
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from services.avito_client import avito_client
        
        try:
            ai_decision = ai_decision_engine.process_conversation(
                chat_id=chat_id,
                new_messages=context['new_messages'],
                history=context['history']
            )
            
            logger.info(f"AI decision for {chat_id}: {ai_decision}")
            
            response_text = ai_decision.get('response', 'THX!')
            
            result = avito_client.send_message(414329950, chat_id, response_text)
            
            if result:
                logger.info(f"Response sent: {response_text}")
                
                if ai_decision.get('needs_price_calculation', False):
                    logger.info(f"Sending to price calculator for chat {chat_id}")
            else:
                logger.error("Failed to send response")
                
        except Exception as e:
            logger.error(f"AI processing error: {e}")
    
    def mark_messages_queued(self, messages: List[Dict]):
        try:
            conn = psycopg2.connect(**self.db_config)
            with conn.cursor() as cursor:
                for msg in messages:
                    cursor.execute("""
                        UPDATE simple_messages 
                        SET ai_processed = TRUE, processed_at = NOW()
                        WHERE message_id = %s
                    """, (msg['message_id'],))
                conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error marking messages as queued: {e}")

message_accumulator = MessageAccumulator()
