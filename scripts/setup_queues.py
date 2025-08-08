#!/usr/bin/env python3

import pika
import sys

def create_project_queues():
    """Создание всех очередей для проекта"""
    try:
        print("🔍 Подключаемся к RabbitMQ для создания очередей...")
        
        uri = 'amqp://Tim:AVITOPassw0rd@85.193.95.165:5672/Avito'
        connection = pika.BlockingConnection(pika.URLParameters(uri))
        channel = connection.channel()
        
        # Список всех очередей проекта
        queues = [
            'avito.messages.incoming',
            'avito.ai.processing', 
            'avito.messages.outgoing',
            'avito.price.calculate',
            'avito.admin.notifications',
            'avito.amocrm.sync'
        ]
        
        print("📋 Создаем очереди:")
        for queue_name in queues:
            channel.queue_declare(queue=queue_name, durable=True)
            print(f"  ✅ {queue_name}")
        
        connection.close()
        print(f"\n🎉 Успешно создано {len(queues)} очередей!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания очередей: {e}")
        return False

if __name__ == "__main__":
    success = create_project_queues()
    if not success:
        sys.exit(1)
