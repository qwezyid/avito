#!/usr/bin/env python3

import redis
import json
from datetime import datetime

def test_redis_operations():
    """Тест основных операций Redis"""
    print("🔍 Тестируем операции Redis...")
    
    try:
        r = redis.Redis(
            host="31.130.151.91",
            port=6379,
            username="Tim",
            password="AVITOPassw0rd",
            decode_responses=True
        )
        
        # Тест 1: Простая запись/чтение
        test_key = "test:chat:12345"
        test_data = {
            "chat_id": "12345",
            "stage": "greeting",
            "last_message": "Привет!",
            "timestamp": datetime.now().isoformat()
        }
        
        r.setex(test_key, 60, json.dumps(test_data, ensure_ascii=False))
        print("✅ Запись данных в Redis")
        
        # Чтение данных
        stored_data = r.get(test_key)
        if stored_data:
            parsed_data = json.loads(stored_data)
            print(f"✅ Чтение данных: chat_id = {parsed_data['chat_id']}")
        
        # Удаление тестовых данных
        r.delete(test_key)
        print("✅ Удаление тестовых данных")
        
        print("🎉 Redis операции работают корректно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка Redis операций: {e}")
        return False

if __name__ == "__main__":
    test_redis_operations()
