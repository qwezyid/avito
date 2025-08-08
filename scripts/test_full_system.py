#!/usr/bin/env python3

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.redis_manager import redis_session_manager
from src.core.rabbitmq_manager import rabbitmq_manager
from src.core.system_coordinator import system_coordinator

def test_full_system():
    """Полный тест всей системы"""
    print("🚀 Полное тестирование системы Avito AI Assistant\n")
    
    results = []
    
    # Тест 1: Redis
    print("1️⃣ Тестируем Redis...")
    try:
        test_session = redis_session_manager.create_new_session('full_test_123')
        if test_session:
            print("  ✅ Redis работает")
            results.append(True)
        else:
            print("  ❌ Redis не работает")
            results.append(False)
    except Exception as e:
        print(f"  ❌ Redis ошибка: {e}")
        results.append(False)
    
    # Тест 2: RabbitMQ
    print("2️⃣ Тестируем RabbitMQ...")
    try:
        success = rabbitmq_manager.send_message('incoming_messages', {
            'chat_id': 'full_test_123',
            'text': 'Системный тест'
        })
        if success:
            print("  ✅ RabbitMQ работает")
            results.append(True)
        else:
            print("  ❌ RabbitMQ не работает")
            results.append(False)
    except Exception as e:
        print(f"  ❌ RabbitMQ ошибка: {e}")
        results.append(False)
    
    # Тест 3: Координатор
    print("3️⃣ Тестируем координатор...")
    try:
        health = system_coordinator.check_system_health()
        if health['status'] in ['healthy', 'degraded']:
            print("  ✅ Координатор работает")
            results.append(True)
        else:
            print("  ❌ Координатор не работает")
            results.append(False)
    except Exception as e:
        print(f"  ❌ Координатор ошибка: {e}")
        results.append(False)
    
    # Тест 4: Интеграция компонентов
    print("4️⃣ Тестируем интеграцию...")
    try:
        # Создаем сессию в Redis
        session = redis_session_manager.create_new_session('integration_test')
        
        # Отправляем сообщение в RabbitMQ
        message_sent = rabbitmq_manager.send_message('ai_processing', {
            'chat_id': 'integration_test',
            'message': 'Тест интеграции',
            'stage': 'greeting'
        })
        
        # Обновляем сессию
        updated = redis_session_manager.add_message_to_history(
            'integration_test', 
            'Тест интеграции', 
            'in'
        )
        
        if session and message_sent and updated:
            print("  ✅ Интеграция работает")
            results.append(True)
        else:
            print("  ❌ Интеграция не работает")
            results.append(False)
            
    except Exception as e:
        print(f"  ❌ Интеграция ошибка: {e}")
        results.append(False)
    
    # Очистка тестовых данных
    print("5️⃣ Очищаем тестовые данные...")
    try:
        redis_session_manager.delete_chat_session('full_test_123')
        redis_session_manager.delete_chat_session('integration_test')
        print("  ✅ Тестовые данные очищены")
    except Exception as e:
        print(f"  ⚠️ Ошибка очистки: {e}")
    
    # Результаты
    print(f"\n📊 Результаты тестирования: {sum(results)}/4 компонентов работают")
    
    if all(results):
        print("🎉 ВСЯ СИСТЕМА РАБОТАЕТ КОРРЕКТНО!")
        print("✅ Готова к следующему этапу разработки")
        return True
    else:
        print("⚠️ Есть проблемы в системе")
        return False

if __name__ == "__main__":
    success = test_full_system()
    if not success:
        sys.exit(1)
