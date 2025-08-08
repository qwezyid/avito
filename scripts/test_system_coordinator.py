#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.system_coordinator import system_coordinator
from src.core.rabbitmq_manager import rabbitmq_manager

def test_system_coordinator():
    """Тест системного координатора"""
    print("🔍 Тестируем System Coordinator...")
    
    try:
        # Тест 1: Проверка состояния системы
        print("1️⃣ Проверяем состояние системы...")
        health = system_coordinator.check_system_health()
        
        print(f"  📊 Статус системы: {health['status']}")
        for service, status in health['services'].items():
            status_icon = "✅" if status == "healthy" else "❌"
            print(f"  {status_icon} {service}: {status}")
        
        # Тест 2: Симуляция входящего сообщения
        print("2️⃣ Симулируем входящее сообщение...")
        
        test_message = {
            'chat_id': 'test_coord_123',
            'text': 'Привет! Нужна перевозка из Москвы в СПб',
            'author_id': 12345
        }
        
        # Отправляем сообщение в очередь
        success = rabbitmq_manager.send_message('incoming_messages', test_message)
        if success:
            print("  ✅ Тестовое сообщение отправлено в очередь")
        else:
            print("  ❌ Ошибка отправки тестового сообщения")
            return False
        
        # Тест 3: Проверяем информацию об очередях
        print("3️⃣ Проверяем состояние очередей...")
        
        queue_types = ['incoming_messages', 'ai_processing', 'outgoing_messages']
        for queue_type in queue_types:
            info = rabbitmq_manager.get_queue_info(queue_type)
            if info:
                print(f"  📊 {queue_type}: {info['message_count']} сообщений")
            else:
                print(f"  ❌ Ошибка получения информации о {queue_type}")
        
        print("\n🎉 Системный координатор работает корректно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в тестах координатора: {e}")
        return False

if __name__ == "__main__":
    success = test_system_coordinator()
    if not success:
        sys.exit(1)
