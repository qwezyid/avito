import logging
import threading
import time
from datetime import datetime
from typing import Dict

from .redis_manager import redis_session_manager
from .rabbitmq_manager import rabbitmq_manager
from ..services.avito_client import avito_client

logger = logging.getLogger('system_coordinator')

class SystemCoordinator:
    """Главный координатор всей системы"""
    
    def __init__(self):
        self.running = False
        self.services_status = {
            'redis': False,
            'rabbitmq': False,
            'database': False
        }
        
        # Регистрируем обработчики для всех очередей
        self._register_handlers()
    
    def _register_handlers(self):
        """Регистрация всех обработчиков очередей"""
        
        # Обработчик входящих сообщений от Avito
        rabbitmq_manager.register_handler('incoming_messages', self.handle_incoming_message)
        
        # Обработчик ИИ обработки
        rabbitmq_manager.register_handler('ai_processing', self.handle_ai_processing)
        
        # Обработчик исходящих сообщений
        rabbitmq_manager.register_handler('outgoing_messages', self.handle_outgoing_message)
        
        # Обработчик расчета цен
        rabbitmq_manager.register_handler('price_calculation', self.handle_price_calculation)
        
        # Обработчик уведомлений админов
        rabbitmq_manager.register_handler('admin_notifications', self.handle_admin_notification)
        
        # Обработчик синхронизации с AmoCRM
        rabbitmq_manager.register_handler('amocrm_sync', self.handle_amocrm_sync)
        
        logger.info("Все обработчики зарегистрированы")
    
    def handle_incoming_message(self, message_data: Dict) -> bool:
        """Обработка входящего сообщения от пользователя"""
        try:
            chat_id = message_data.get('chat_id')
            user_message = message_data.get('text', '')
            
            logger.info(f"Обрабатываем входящее сообщение от чата {chat_id}")
            
            # Получаем или создаем сессию
            session = redis_session_manager.get_chat_session(chat_id)
            if not session:
                session = redis_session_manager.create_new_session(chat_id)
                logger.info(f"Создана новая сессия для чата {chat_id}")
            
            # Добавляем сообщение в историю
            redis_session_manager.add_message_to_history(chat_id, user_message, 'in')
            
            # Отправляем на ИИ обработку
            ai_task = {
                'chat_id': chat_id,
                'message': user_message,
                'current_stage': session['ai_stage'],
                'extracted_data': session['extracted_data']
            }
            
            return rabbitmq_manager.send_message('ai_processing', ai_task)
            
        except Exception as e:
            logger.error(f"Ошибка обработки входящего сообщения: {e}")
            return False
    
    def handle_ai_processing(self, message_data: Dict) -> bool:
        """Обработка задачи ИИ"""
        try:
            chat_id = message_data.get('chat_id')
            user_message = message_data.get('message', '')
            current_stage = message_data.get('current_stage', 'greeting')
            
            logger.info(f"ИИ обработка для чата {chat_id}, этап: {current_stage}")
            
            # Здесь будет вызов ИИ API (OpenRouter)
            # Пока что имитируем ответ
            ai_response = self._simulate_ai_response(user_message, current_stage)
            
            # Обновляем сессию с ответом ИИ
            session = redis_session_manager.get_chat_session(chat_id)
            if session:
                session['last_ai_response'] = ai_response['text']
                redis_session_manager.save_chat_session(chat_id, session)
            
            # Отправляем ответ пользователю
            outgoing_task = {
                'chat_id': chat_id,
                'message': ai_response['text'],
                'message_type': 'text'
            }
            
            return rabbitmq_manager.send_message('outgoing_messages', outgoing_task)
            
        except Exception as e:
            logger.error(f"Ошибка ИИ обработки: {e}")
            return False
    
    def handle_outgoing_message(self, message_data: Dict) -> bool:
        try:
            chat_id = message_data.get('chat_id')
            message_text = message_data.get('message', '')
            user_id = message_data.get('user_id', 414329950)  # Replace with real user_id
            
            logger.info(f"Sending message to chat {chat_id}")

            result = avito_client.send_message(user_id, chat_id, message_text)
            
            if result:
                redis_session_manager.add_message_to_history(chat_id, message_text, 'out')
                logger.info("Message sent successfully")
                return True
            else:
                logger.error("Failed to send message via Avito API")
                return False
                
        except Exception as e:
            logger.error(f"error: {e}")
            return False
    
    def handle_price_calculation(self, message_data: Dict) -> bool:
        """Обработка расчета стоимости"""
        try:
            logger.info("Обрабатываем запрос на расчет стоимости")
            
            # Здесь будет логика расчета цены
            calculated_price = 15000  # Заглушка
            
            # Уведомляем админов
            admin_task = {
                'type': 'price_approval',
                'chat_id': message_data.get('chat_id'),
                'calculated_price': calculated_price,
                'route_data': message_data
            }
            
            return rabbitmq_manager.send_message('admin_notifications', admin_task)
            
        except Exception as e:
            logger.error(f"Ошибка расчета цены: {e}")
            return False
    
    def handle_admin_notification(self, message_data: Dict) -> bool:
        """Обработка уведомлений админов"""
        try:
            notification_type = message_data.get('type')
            logger.info(f"Отправляем уведомление админам: {notification_type}")
            
            # Здесь будет отправка в Telegram
            return True
            
        except Exception as e:
            logger.error(f"Ошибка уведомления админов: {e}")
            return False
    
    def handle_amocrm_sync(self, message_data: Dict) -> bool:
        """Обработка синхронизации с AmoCRM"""
        try:
            logger.info("Синхронизируем данные с AmoCRM")
            
            # Здесь будет интеграция с AmoCRM API
            return True
            
        except Exception as e:
            logger.error(f"Ошибка синхронизации AmoCRM: {e}")
            return False
    
    def _simulate_ai_response(self, user_message: str, stage: str) -> Dict:
        """Имитация ответа ИИ (временная заглушка)"""
        responses = {
            'greeting': "Добро пожаловать! Помогу организовать перевозку. Откуда и куда нужно везти груз?",
            'route_collection': "Спасибо за информацию о маршруте. Расскажите о грузе - что везем, вес, габариты?",
            'cargo_details': "Понятно. Какой транспорт предпочитаете? Рассчитываю стоимость...",
            'price_calculation': "Стоимость перевозки рассчитывается. Скоро предоставлю точную цену."
        }
        
        return {
            'text': responses.get(stage, "Спасибо за сообщение. Обрабатываю запрос..."),
            'next_stage': stage
        }
    
    def start_service(self, queue_type: str):
        """Запуск обработки конкретной очереди"""
        def run_consumer():
            logger.info(f"Запускаем сервис для очереди {queue_type}")
            rabbitmq_manager.start_consuming(queue_type)
        
        thread = threading.Thread(target=run_consumer, daemon=True)
        thread.start()
        return thread
    
    def check_system_health(self) -> Dict:
        """Проверка состояния всей системы"""
        health = {
            'timestamp': datetime.now().isoformat(),
            'status': 'healthy',
            'services': {}
        }
        
        # Проверяем Redis
        try:
            test_session = redis_session_manager.get_chat_session('health_check')
            health['services']['redis'] = 'healthy'
        except:
            health['services']['redis'] = 'unhealthy'
            health['status'] = 'degraded'
        
        # Проверяем RabbitMQ
        try:
            info = rabbitmq_manager.get_queue_info('incoming_messages')
            health['services']['rabbitmq'] = 'healthy' if info else 'unhealthy'
        except:
            health['services']['rabbitmq'] = 'unhealthy'
            health['status'] = 'degraded'
        
        return health

# Глобальный экземпляр
system_coordinator = SystemCoordinator()
