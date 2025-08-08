#!/usr/bin/env python3

import sys
import os
import threading
import signal
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.system_coordinator import system_coordinator
from src.core.rabbitmq_manager import rabbitmq_manager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ai_assistant')

class AIAssistantService:
    def __init__(self):
        self.threads = []
        self.running = False
    
    def start_all_services(self):
        self.running = True
        logger.info("Starting AI Assistant services...")
        
        # Запускаем обработчики очередей
        services = [
            'incoming_messages',
            'ai_processing',
            'outgoing_messages',
            'price_calculation',
            'admin_notifications'
        ]
        
        for service in services:
            thread = threading.Thread(
                target=self.start_queue_consumer,
                args=(service,),
                daemon=True
            )
            thread.start()
            self.threads.append(thread)
            logger.info(f"Started {service} consumer")
        
        logger.info("All services started successfully")
    
    def start_queue_consumer(self, queue_type: str):
        try:
            rabbitmq_manager.start_consuming(queue_type)
        except Exception as e:
            logger.error(f"Error in {queue_type} consumer: {e}")
    
    def stop_all_services(self):
        self.running = False
        logger.info("Stopping all services...")
        rabbitmq_manager.stop_consuming()

def signal_handler(signum, frame):
    logger.info("Received shutdown signal")
    assistant.stop_all_services()
    sys.exit(0)

if __name__ == "__main__":
    assistant = AIAssistantService()
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    assistant.start_all_services()
    
    try:
        while assistant.running:
            time.sleep(1)
    except KeyboardInterrupt:
        assistant.stop_all_services()
