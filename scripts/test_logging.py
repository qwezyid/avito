#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.logger import loggers

def test_logging():
    """Тест системы логирования"""
    print("🔍 Тестируем систему логирования...")
    
    try:
        # Тестируем разные уровни логов
        loggers['redis'].info("Тестовое сообщение Redis")
        loggers['rabbitmq'].info("Тестовое сообщение RabbitMQ")
        loggers['database'].warning("Тестовое предупреждение БД")
        loggers['ai'].error("Тестовая ошибка ИИ")
        
        print("✅ Логирование работает")
        print("📁 Проверьте файл logs/avito_bot.log")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка логирования: {e}")
        return False

if __name__ == "__main__":
    test_logging()
