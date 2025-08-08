import logging
import requests
import json
from typing import Dict, List, Optional

logger = logging.getLogger('ai_decision_engine')

class AIDecisionEngine:
    def __init__(self):
        # Пример API-ключа (замените на настоящий)
        self.openrouter_api_key = "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"
        self.model = "nousresearch/nous-hermes-2-mixtral-8x7b-dpo"  # Используем другую модель
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
    
    def process_conversation(self, chat_id: str, new_messages: str, history: List[Dict]) -> Dict:
        
        system_prompt = """Ты менеджер по автоперевозкам. Твоя задача - собрать информацию для расчета стоимости и отправить на калькулятор.

НУЖНАЯ ИНФОРМАЦИЯ ДЛЯ РАСЧЕТА:
- Маршрут (откуда - куда)
- Тип груза 
- Вес/объем груза

ПРАВИЛА ОБЩЕНИЯ:
- Пиши коротко, как человек
- Никакой воды и длинных текстов
- Задавай по одному вопросу за раз
- Будь дружелюбным но деловым

КОГДА У ТЕБЯ ЕСТЬ ВСЯ ИНФОРМАЦИЯ - отвечай "Рассчитываю стоимость" и установи needs_price_calculation: true

Отвечай СТРОГО в JSON:
{
    "response": "твой короткий ответ",
    "needs_price_calculation": true/false,
    "has_all_info": true/false
}"""

        conversation_context = self.build_conversation_context(new_messages, history)
        
        try:
            ai_response = self.call_llm_api(system_prompt, conversation_context)
            return ai_response
        except Exception as e:
            logger.error(f"LLM API error: {e}")
            return {
                "response": "Привет! Откуда и куда нужна перевозка?",
                "needs_price_calculation": False,
                "has_all_info": False
            }
    
    def build_conversation_context(self, new_messages: str, history: List[Dict]) -> str:
        context_parts = []
        
        if history:
            for msg in history[-6:]:  # Только последние 6 сообщений
                # Проверяем, что сообщение не от нашего бота (если есть author_id)
                if 'author_id' in msg and msg.get('author_id') == 414329950:
                    role = "Менеджер"
                else:
                    role = "Клиент" if msg.get('role', '') == 'user' else "Менеджер"
                
                content = msg.get('content', '')
                context_parts.append(f"{role}: {content}")
        
        context_parts.append(f"Клиент (новое): {new_messages}")
        
        return "\n".join(context_parts)
    
    def call_llm_api(self, system_prompt: str, context: str) -> Dict:
        # Проверяем ключ - если нет, используем заглушку
        if not self.openrouter_api_key or self.openrouter_api_key == "your_openrouter_key_here":
            return self.simulate_ai_response(context)
        
        try:
            headers = {
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://avito.ru",  # Добавляем обязательные поля
                "X-Title": "AvitoAssistant"  
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": context}
                ],
                "max_tokens": 300,
                "temperature": 0.7
            }
            
            # Отладочная информация
            logger.info(f"Sending request to OpenRouter, model: {self.model}")
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,  # Используем json вместо data=json.dumps()
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info("OpenRouter response received successfully")
                ai_text = data["choices"][0]["message"]["content"]
                
                # Парсим JSON ответ
                try:
                    return json.loads(ai_text)
                except Exception as e:
                    logger.error(f"JSON parsing error: {e}, raw text: {ai_text[:100]}...")
                    return {
                        "response": "Привет! Откуда и куда нужна перевозка?",
                        "needs_price_calculation": False,
                        "has_all_info": False
                    }
            else:
                logger.error(f"API error: {response.status_code}, response: {response.text}")
                # Вместо вызова исключения возвращаем заглушку
                return self.simulate_ai_response(context)
                
        except Exception as e:
            logger.error(f"Request error: {e}")
            # Если что-то пошло не так, возвращаем заглушку
            return self.simulate_ai_response(context)
    
    def simulate_ai_response(self, context: str) -> Dict:
        """Умная заглушка для тестирования"""
        context_lower = context.lower()
        
        # Улучшенная логика определения содержимого контекста
        route_keywords = ['из', 'от', 'до', 'в', 'москва', 'москвы', 'спб', 'питер', 'питера', 'екатеринбург']
        cargo_keywords = ['кг', 'тонн', 'груз', 'мебель', 'коробки', 'авто', 'камри', 'машина', 'автомобиль']
        greeting_keywords = ['привет', 'здравствуйте', 'добрый', 'здорово']
        
        # Проверка на явное указание маршрута
        has_moscow = 'москв' in context_lower 
        has_spb = 'питер' in context_lower or 'спб' in context_lower
        has_explicit_route = has_moscow and has_spb
        
        # Общие проверки
        has_route = has_explicit_route or any(word in context_lower for word in route_keywords)
        has_cargo = any(word in context_lower for word in cargo_keywords)
        has_greeting = any(word in context_lower for word in greeting_keywords)
        
        # Логика ответов
        if 'рассчитываю стоимость' in context_lower:
            return {
                "response": "Понял, ожидайте расчет",
                "needs_price_calculation": False,
                "has_all_info": True
            }
        
        # Явно выделяем проверку маршрута Москва-Питер
        if has_explicit_route:
            if has_cargo:
                return {
                    "response": "Рассчитываю стоимость перевозки из Москвы в Питер",
                    "needs_price_calculation": True,
                    "has_all_info": True
                }
            else:
                return {
                    "response": "Понял маршрут Москва-Питер. Что планируете перевозить?",
                    "needs_price_calculation": False,
                    "has_all_info": False
                }
        
        if has_route and has_cargo:
            return {
                "response": "Рассчитываю стоимость",
                "needs_price_calculation": True,
                "has_all_info": True
            }
        
        if has_greeting or not has_route:
            return {
                "response": "Привет! Откуда и куда нужна перевозка?",
                "needs_price_calculation": False,
                "has_all_info": False
            }
        
        if has_route and not has_cargo:
            return {
                "response": "Понял маршрут. Что везем и сколько весит?",
                "needs_price_calculation": False,
                "has_all_info": False
            }
        
        # Дефолтный ответ
        return {
            "response": "Уточните детали перевозки",
            "needs_price_calculation": False,
            "has_all_info": False
        }


# Инициализация глобального экземпляра
ai_decision_engine = AIDecisionEngine()
