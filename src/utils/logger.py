import logging
import os
from datetime import datetime

def setup_logging():
    """Настройка системы логирования"""
    
    # Создаем директорию для логов если не существует
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Формат логов
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Настройка основного логгера
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            # Логи в файл
            logging.FileHandler(f'{log_dir}/avito_bot.log'),
            # Логи в консоль
            logging.StreamHandler()
        ]
    )
    
    # Отдельные логгеры для разных компонентов
    loggers = {
        'redis': logging.getLogger('redis_manager'),
        'rabbitmq': logging.getLogger('rabbitmq_manager'),
        'database': logging.getLogger('database_manager'),
        'ai': logging.getLogger('ai_processor'),
        'avito_api': logging.getLogger('avito_api')
    }
    
    return loggers

# Инициализируем логгеры
loggers = setup_logging()
