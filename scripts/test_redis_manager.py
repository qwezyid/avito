#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.redis_manager import redis_session_manager

def test_session_operations():
    """Тест всех операций с сессиями"""
    print("🔍 Тестируем Redis Session Manager...")
    
    chat_id = "test_chat_12345"
    
    try:
        # Тест 1: Создание новой сессии
        print("1️⃣ Создаем новую сессию...")
        session = redis_session_manager.create_new_session(chat_id)
        if session and session['chat_id'] == chat_id:
            print("✅ Сессия создана успешно")
        else:
            print("❌ Ошибка создания сессии")
            return False
        
        # Тест 2: Получение сессии
        print("2️⃣ Получаем сессию...")
        retrieved_session = redis_session_manager.get_chat_session(chat_id)
        if retrieved_session and retrieved_session['chat_id'] == chat_id:
            print("✅ Сессия получена успешно")
        else:
            print("❌ Ошибка получения сессии")
            return False
        
        # Тест 3: Добавление сообщения
        print("3️⃣ Добавляем сообщение в историю...")
        success = redis_session_manager.add_message_to_history(
            chat_id, 
            "Привет! Нужна перевозка груза", 
            "in"
        )
        if success:
            print("✅ Сообщение добавлено")
        else:
            print("❌ Ошибка добавления сообщения")
            return False
        
        # Тест 4: Обновление этапа
        print("4️⃣ Обновляем этап ИИ...")
        success = redis_session_manager.update_chat_stage(chat_id, "route_collection")
        if success:
            print("✅ Этап обновлен")
        else:
            print("❌ Ошибка обновления этапа")
            return False
        
        # Тест 5: Обновление извлеченных данных
        print("5️⃣ Обновляем извлеченные данные...")
        success = redis_session_manager.update_extracted_data(chat_id, {
            'route_from': 'Москва',
            'cargo_type': 'мебель'
        })
        if success:
            print("✅ Данные обновлены")
        else:
            print("❌ Ошибка обновления данных")
            return False
        
        # Тест 6: Проверка итогового состояния
        print("6️⃣ Проверяем итоговое состояние...")
        final_session = redis_session_manager.get_chat_session(chat_id)
        
        checks = [
            final_session['ai_stage'] == 'route_collection',
            final_session['extracted_data']['route_from'] == 'Москва',
            final_session['extracted_data']['cargo_type'] == 'мебель',
            len(final_session['conversation_history']) == 1,
            final_session['messages_count'] == 1
        ]
        
        if all(checks):
            print("✅ Все данные корректны")
        else:
            print("❌ Данные не соответствуют ожиданиям")
            print(f"Сессия: {final_session}")
            return False
        
        # Тест 7: Получение активных чатов
        print("7️⃣ Получаем список активных чатов...")
        active_chats = redis_session_manager.get_active_chats()
        if len(active_chats) > 0:
            print(f"✅ Найдено {len(active_chats)} активных чатов")
        else:
            print("⚠️ Активные чаты не найдены")
        
        # Тест 8: Удаление тестовой сессии
        print("8️⃣ Удаляем тестовую сессию...")
        success = redis_session_manager.delete_chat_session(chat_id)
        if success:
            print("✅ Сессия удалена")
        else:
            print("❌ Ошибка удаления сессии")
        
        print("\n🎉 Все тесты Redis Session Manager прошли успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в тестах: {e}")
        return False

if __name__ == "__main__":
    success = test_session_operations()
    if not success:
        sys.exit(1)
