#!/usr/bin/env python3

import sys
import os
import time
import threading
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.avito_client import avito_client
from src.core.rabbitmq_manager import rabbitmq_manager
import logging

logger = logging.getLogger('avito_poller')

class AvitoPoller:
    def __init__(self, user_id: int, poll_interval: int = 30):
        self.user_id = user_id
        self.poll_interval = poll_interval
        self.processed_messages = set()
        self.running = False
    
    def start_polling(self):
        self.running = True
        logger.info(f"Started polling for user {self.user_id}")
        
        while self.running:
            try:
                self.poll_new_messages()
                time.sleep(self.poll_interval)
            except Exception as e:
                logger.error(f"Polling error: {e}")
                time.sleep(5)
    
    def stop_polling(self):
        self.running = False
    
    def poll_new_messages(self):
        chats = avito_client.get_chats(self.user_id, limit=20)
        if not chats:
            return
        
        for chat in chats:
            chat_id = chat['id']
            messages = avito_client.get_messages(self.user_id, chat_id, limit=5)
            
            if messages:
                for message in messages:
                    if self.is_new_incoming_message(message):
                        self.process_new_message(chat_id, message)
    
    def is_new_incoming_message(self, message) -> bool:
        message_id = message.get('id')
        direction = message.get('direction')
        
        return (message_id not in self.processed_messages and 
                direction == 'in' and
                message.get('content', {}).get('text'))
    
    def process_new_message(self, chat_id: str, message):
        message_id = message['id']
        
        message_data = {
            'chat_id': chat_id,
            'message_id': message_id,
            'author_id': message.get('author_id'),
            'text': message.get('content', {}).get('text', ''),
            'created': message.get('created'),
            'direction': message.get('direction'),
            'type': message.get('type'),
            'user_id': self.user_id
        }
        
        success = rabbitmq_manager.send_message('incoming_messages', message_data)
        if success:
            self.processed_messages.add(message_id)
            logger.info(f"New message queued: {message_id}")

if __name__ == "__main__":
    poller = AvitoPoller(user_id=414329950)  # Replace with real user_id
    
    try:
        poller.start_polling()
    except KeyboardInterrupt:
        print("Stopping poller...")
        poller.stop_polling()
