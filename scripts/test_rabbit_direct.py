#!/usr/bin/env python3

import pika
import sys

def test_rabbit_connection():
    """Прямой тест подключения к RabbitMQ"""
    try:
        print("🔍 Подключаемся к RabbitMQ...")
        
        uri = 'amqp://Tim:AVITOPassw0rd@85.193.95.165:5672/Avito'
        connection = pika.BlockingConnection(pika.URLParameters(uri))
        channel = connection.channel()
        
        print("✅ Подключение к RabbitMQ успешно!")
        
        # Создаем тестовую очередь
        test_queue = 'test_queue'
        channel.queue_declare(queue=test_queue, durable=True)
        print(f"✅ Тестовая очередь '{test_queue}' создана")
        
        # Отправляем тестовое сообщение
        channel.basic_publish(
            exchange='',
            routing_key=test_queue,
            body='Hello RabbitMQ!',
            properties=pika.BasicProperties(delivery_mode=2)
        )
        print("✅ Тестовое сообщение отправлено")
        
        # Удаляем тестовую очередь
        channel.queue_delete(queue=test_queue)
        print("✅ Тестовая очередь удалена")
        
        connection.close()
        print("✅ Соединение закрыто")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    success = test_rabbit_connection()
    if success:
        print("\n🎉 RabbitMQ работает корректно!")
    else:
        print("\n⚠️ Проблемы с RabbitMQ")
        sys.exit(1)
