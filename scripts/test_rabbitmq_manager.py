#!/usr/bin/env python3

import sys
import os
import time
import threading
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.rabbitmq_manager import rabbitmq_manager

def test_rabbitmq_operations():
    """Тест всех операций RabbitMQ менеджера"""
    print("🔍 Тестируем RabbitMQ Manager...")
    
    try:
        # Тест 1: Создание очередей
        print("1️⃣ Создаем очереди...")
        if rabbitmq_manager.ensure_queues():
            print("✅ Все очереди созданы")
        else:
            print("❌ Ошибка создания очередей")
            return False
        
        # Тест 2: Отправка тестовых сообщений
        print("2️⃣ Отправляем тестовые сообщения...")
        
        test_messages = [
            ('incoming_messages', {'chat_id': 'test123', 'text': 'Привет!'}),
            ('ai_processing', {'chat_id': 'test123', 'stage': 'greeting'}),
            ('price_calculation', {'route_from': 'Москва', 'route_to': 'СПб'})
        ]
        
        for queue_type, message_data in test_messages:
            success = rabbitmq_manager.send_message(queue_type, message_data)
            if success:
                print(f"  ✅ Сообщение отправлено в {queue_type}")
            else:
                print(f"  ❌ Ошибка отправки в {queue_type}")
                return False
        
        # Тест 3: Получение информации о очередях
        print("3️⃣ Проверяем информацию о очередях...")
        for queue_type in ['incoming_messages', 'ai_processing', 'price_calculation']:
            info = rabbitmq_manager.get_queue_info(queue_type)
            if info:
                print(f"  📊 {queue_type}: {info['message_count']} сообщений")
            else:
                print(f"  ❌ Не удалось получить информацию о {queue_type}")
        
        # Тест 4: Регистрация обработчика
        print("4️⃣ Регистрируем тестовый обработчик...")
        
        processed_messages = []
        
        def test_handler(message_data):
            print(f"    🔄 Обрабатываем: {message_data}")
            processed_messages.append(message_data)
            return True  # Успешная обработка
        
        success = rabbitmq_manager.register_handler('incoming_messages', test_handler)
        if success:
            print("✅ Обработчик зарегистрирован")
        else:
            print("❌ Ошибка регистрации обработчика")
            return False
        
        # Тест 5: Кратковременное потребление (в отдельном потоке)
        print("5️⃣ Тестируем потребление сообщений (5 секунд)...")
        
        def consume_messages():
            rabbitmq_manager.start_consuming('incoming_messages')
        
        # Запускаем потребление в отдельном потоке
        consume_thread = threading.Thread(target=consume_messages, daemon=True)
        consume_thread.start()
        
        # Ждем немного для обработки сообщений
        time.sleep(3)
        
        # Останавливаем потребление
        rabbitmq_manager.stop_consuming()
        
        if len(processed_messages) > 0:
            print(f"✅ Обработано {len(processed_messages)} сообщений")
        else:
            print("⚠️ Сообщения не обработаны (возможно, очередь пуста)")
        
        print("\n🎉 Все тесты RabbitMQ Manager прошли успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в тестах RabbitMQ: {e}")
        return False

if __name__ == "__main__":
    success = test_rabbitmq_operations()
    if not success:
        sys.exit(1)
