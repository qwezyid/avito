import pika
import json
import logging
from datetime import datetime
from typing import Dict, Callable, Optional
import time

logger = logging.getLogger('rabbitmq_manager')

class RabbitMQManager:
   def __init__(self):
       self.uri = 'amqp://Tim:AVITOPassw0rd@85.193.95.165:5672/Avito'
       self.connection = None
       self.channel = None
       
       # Определяем все очереди проекта
       self.queues = {
           'incoming_messages': 'avito.messages.incoming',
           'ai_processing': 'avito.ai.processing',
           'outgoing_messages': 'avito.messages.outgoing',
           'price_calculation': 'avito.price.calculate',
           'admin_notifications': 'avito.admin.notifications',
           'amocrm_sync': 'avito.amocrm.sync'
       }
       
       # Обработчики для каждой очереди
       self.handlers = {}
   
   def connect(self) -> bool:
       """Подключение к RabbitMQ"""
       try:
           self.connection = pika.BlockingConnection(
               pika.URLParameters(self.uri)
           )
           self.channel = self.connection.channel()
           self.channel.basic_qos(prefetch_count=1)
           
           logger.info("Успешное подключение к RabbitMQ")
           return True
       except Exception as e:
           logger.error(f"Ошибка подключения к RabbitMQ: {e}")
           return False
   
   def disconnect(self):
       """Закрытие подключения"""
       try:
           if self.channel and not self.channel.is_closed:
               self.channel.close()
           if self.connection and not self.connection.is_closed:
               self.connection.close()
           logger.info("Подключение к RabbitMQ закрыто")
       except Exception as e:
           logger.error(f"Ошибка закрытия подключения: {e}")
   
   def ensure_queues(self) -> bool:
       """Создание всех очередей проекта (упрощенная версия)"""
       if not self.connect():
           return False
           
       try:
           for queue_type, queue_name in self.queues.items():
               # Простое объявление очереди без дополнительных параметров
               self.channel.queue_declare(queue=queue_name, durable=True)
               logger.info(f"Очередь {queue_name} готова")
           
           return True
       except Exception as e:
           logger.error(f"Ошибка создания очередей: {e}")
           return False
       finally:
           self.disconnect()
   
   def send_message(self, queue_type: str, message_data: Dict) -> bool:
       """Отправка сообщения в очередь"""
       if not self.connect():
           return False
           
       try:
           queue_name = self.queues.get(queue_type)
           if not queue_name:
               logger.error(f"Неизвестный тип очереди: {queue_type}")
               return False
           
           # Простое сообщение
           message = {
               'data': message_data,
               'timestamp': datetime.now().isoformat(),
               'queue_type': queue_type
           }
           
           self.channel.basic_publish(
               exchange='',
               routing_key=queue_name,
               body=json.dumps(message, ensure_ascii=False),
               properties=pika.BasicProperties(delivery_mode=2)
           )
           
           logger.info(f"Сообщение отправлено в {queue_name}")
           return True
           
       except Exception as e:
           logger.error(f"Ошибка отправки сообщения в {queue_type}: {e}")
           return False
       finally:
           self.disconnect()
   
   def register_handler(self, queue_type: str, handler_function: Callable) -> bool:
       """Регистрация обработчика для типа очереди"""
       if queue_type not in self.queues:
           logger.error(f"Неизвестный тип очереди: {queue_type}")
           return False
       
       self.handlers[queue_type] = handler_function
       logger.info(f"Обработчик зарегистрирован для {queue_type}")
       return True
   
   def get_queue_info(self, queue_type: str) -> Optional[Dict]:
       """Получение информации о очереди"""
       if not self.connect():
           return None
           
       try:
           queue_name = self.queues.get(queue_type)
           if not queue_name:
               return None
           
           method = self.channel.queue_declare(queue=queue_name, passive=True)
           
           return {
               'queue_name': queue_name,
               'message_count': method.method.message_count,
               'consumer_count': method.method.consumer_count
           }
       except Exception as e:
           logger.error(f"Ошибка получения информации о очереди {queue_type}: {e}")
           return None
       finally:
           self.disconnect()
   
   def start_consuming(self, queue_type: str) -> bool:
       """Запуск потребления сообщений из конкретной очереди"""
       if queue_type not in self.handlers:
           logger.error(f"Нет обработчика для {queue_type}")
           return False
       
       if not self.connect():
           return False
       
       try:
           queue_name = self.queues[queue_type]
           handler = self.handlers[queue_type]
           
           def message_callback(ch, method, properties, body):
               try:
                   # Парсим сообщение
                   message = json.loads(body)
                   logger.info(f"Получено сообщение из {queue_name}")
                   
                   # Вызываем обработчик
                   result = handler(message['data'])
                   
                   if result:
                       # Подтверждаем обработку
                       ch.basic_ack(delivery_tag=method.delivery_tag)
                       logger.info(f"Сообщение обработано успешно")
                   else:
                       # Отклоняем с повторной постановкой в очередь
                       ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                       logger.warning(f"Сообщение отклонено, вернется в очередь")
                       
               except Exception as e:
                   logger.error(f"Ошибка обработки сообщения: {e}")
                   ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
           
           # Настраиваем потребление
           self.channel.basic_consume(
               queue=queue_name,
               on_message_callback=message_callback
           )
           
           logger.info(f"Начинаем потребление из {queue_name}")
           
           try:
               self.channel.start_consuming()
           except KeyboardInterrupt:
               logger.info("Остановка потребления по запросу пользователя")
               self.channel.stop_consuming()
           
           return True
           
       except Exception as e:
           logger.error(f"Ошибка потребления из {queue_type}: {e}")
           return False
       finally:
           self.disconnect()
   
   def stop_consuming(self):
       """Остановка потребления сообщений"""
       try:
           if self.channel and not self.channel.is_closed:
               self.channel.stop_consuming()
               logger.info("Потребление остановлено")
       except Exception as e:
           logger.error(f"Ошибка остановки потребления: {e}")

# Глобальный экземпляр
rabbitmq_manager = RabbitMQManager()
