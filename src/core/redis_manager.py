import redis
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)

class RedisSessionManager:
    def __init__(self):
        self.redis_client = redis.Redis(
            host="31.130.151.91",
            port=6379,
            username="Tim",
            password="AVITOPassw0rd",
            decode_responses=True
        )
        
        # Префиксы для разных типов данных
        self.prefixes = {
            'chat_session': 'chat:session:',
            'user_data': 'user:data:',
            'ai_context': 'ai:context:',
            'temp_data': 'temp:data:'
        }
    
    def get_chat_session(self, chat_id: str) -> Optional[Dict]:
        """Получает сессию чата из Redis"""
        try:
            session_key = f"{self.prefixes['chat_session']}{chat_id}"
            session_data = self.redis_client.get(session_key)
            
            if session_data:
                return json.loads(session_data)
            return None
        except Exception as e:
            logger.error(f"Ошибка получения сессии {chat_id}: {e}")
            return None
    
    def save_chat_session(self, chat_id: str, session_data: Dict, ttl: int = 3600) -> bool:
        """Сохраняет сессию чата в Redis"""
        try:
            session_key = f"{self.prefixes['chat_session']}{chat_id}"
            
            # Добавляем метаданные
            session_data.update({
                'last_updated': datetime.now().isoformat(),
                'chat_id': chat_id
            })
            
            self.redis_client.setex(
                session_key,
                ttl,
                json.dumps(session_data, ensure_ascii=False)
            )
            
            logger.info(f"Сессия {chat_id} сохранена на {ttl} секунд")
            return True
        except Exception as e:
            logger.error(f"Ошибка сохранения сессии {chat_id}: {e}")
            return False
    
    def create_new_session(self, chat_id: str, initial_data: Dict = None) -> Dict:
        """Создает новую сессию чата"""
        session = {
            'chat_id': chat_id,
            'ai_stage': 'greeting',
            'messages_count': 0,
            'extracted_data': {
                'route_from': None,
                'route_to': None,
                'cargo_type': None,
                'cargo_weight': None,
                'cargo_dimensions': None,
                'transport_type': None,
                'additional_services': [],
                'special_requirements': None
            },
            'conversation_history': [],
            'last_ai_response': None,
            'price_calculation_sent': False,
            'admin_notified': False,
            'created_at': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat()
        }
        
        # Добавляем начальные данные если есть
        if initial_data:
            session.update(initial_data)
        
        self.save_chat_session(chat_id, session)
        logger.info(f"Создана новая сессия для чата {chat_id}")
        
        return session
    
    def update_chat_stage(self, chat_id: str, new_stage: str) -> bool:
        """Обновляет этап ИИ для чата"""
        try:
            session = self.get_chat_session(chat_id)
            if not session:
                logger.warning(f"Сессия {chat_id} не найдена для обновления этапа")
                return False
            
            session['ai_stage'] = new_stage
            session['last_activity'] = datetime.now().isoformat()
            
            return self.save_chat_session(chat_id, session)
        except Exception as e:
            logger.error(f"Ошибка обновления этапа {chat_id}: {e}")
            return False
    
    def add_message_to_history(self, chat_id: str, message: str, direction: str) -> bool:
        """Добавляет сообщение в историю чата"""
        try:
            session = self.get_chat_session(chat_id)
            if not session:
                session = self.create_new_session(chat_id)
            
            # Добавляем сообщение в историю
            message_entry = {
                'text': message,
                'direction': direction,  # 'in' или 'out'
                'timestamp': datetime.now().isoformat()
            }
            
            session['conversation_history'].append(message_entry)
            session['messages_count'] += 1
            session['last_activity'] = datetime.now().isoformat()
            
            # Ограничиваем историю последними 20 сообщениями
            if len(session['conversation_history']) > 20:
                session['conversation_history'] = session['conversation_history'][-20:]
            
            return self.save_chat_session(chat_id, session)
        except Exception as e:
            logger.error(f"Ошибка добавления сообщения {chat_id}: {e}")
            return False
    
    def update_extracted_data(self, chat_id: str, new_data: Dict) -> bool:
        """Обновляет извлеченные ИИ данные"""
        try:
            session = self.get_chat_session(chat_id)
            if not session:
                return False
            
            # Обновляем только те поля, которые не None
            for key, value in new_data.items():
                if value is not None and key in session['extracted_data']:
                    session['extracted_data'][key] = value
            
            session['last_activity'] = datetime.now().isoformat()
            
            return self.save_chat_session(chat_id, session)
        except Exception as e:
            logger.error(f"Ошибка обновления данных {chat_id}: {e}")
            return False
    
    def get_active_chats(self) -> List[Dict]:
        """Получает список всех активных чатов"""
        try:
            pattern = f"{self.prefixes['chat_session']}*"
            chat_keys = self.redis_client.keys(pattern)
            
            active_chats = []
            for key in chat_keys:
                chat_id = key.replace(self.prefixes['chat_session'], "")
                session = self.get_chat_session(chat_id)
                if session:
                    active_chats.append(session)
            
            return active_chats
        except Exception as e:
            logger.error(f"Ошибка получения активных чатов: {e}")
            return []
    
    def delete_chat_session(self, chat_id: str) -> bool:
        """Удаляет сессию чата"""
        try:
            session_key = f"{self.prefixes['chat_session']}{chat_id}"
            result = self.redis_client.delete(session_key)
            
            if result:
                logger.info(f"Сессия {chat_id} удалена")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка удаления сессии {chat_id}: {e}")
            return False

# Глобальный экземпляр
redis_session_manager = RedisSessionManager()
