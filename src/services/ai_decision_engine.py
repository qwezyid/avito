import logging
import requests
import json
from typing import Dict, List, Optional

logger = logging.getLogger('ai_decision_engine')

class AIDecisionEngine:
    def __init__(self):
        self.openrouter_api_key = "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"  # Добавь свой ключ
        self.model = "nousresearch/nous-hermes-2-mixtral-8x7b-dpo"
        self.base_url = "https://openrouter.ai/api/v1"
    
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
                "response": "Извините, произошла ошибка. Чем могу помочь?",
                "needs_price_calculation": False,
                "has_all_info": False
            }
    
    def build_conversation_context(self, new_messages: str, history: List[Dict]) -> str:
        context_parts = []
        
        if history:
            for msg in history[-6:]:  # Только последние 6 сообщений
                role = "Клиент" if msg['role'] == 'user' else "Менеджер"
                context_parts.append(f"{role}: {msg['content']}")
        
        context_parts.append(f"Клиент (новое): {new_messages}")
        
        return "\n".join(context_parts)
    
    def call_llm_api(self, system_prompt: str, context: str) -> Dict:
        
        if not self.openrouter_api_key or self.openrouter_api_key == "your_openrouter_key_here":
            # Заглушка для тестирования без API ключа
            return self.simulate_ai_response(context)
        
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json"
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
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            ai_text = data["choices"][0]["message"]["content"]
            
            # Парсим JSON ответ
            try:
                return json.loads(ai_text)
            except:
                return {
                    "response": ai_text,
                    "needs_price_calculation": False,
                    "has_all_info": False
                }
        else:
            raise Exception(f"API error: {response.status_code}")
    
    def simulate_ai_response(self, context: str) -> Dict:
        """Умная заглушка для тестирования"""
        context_lower = context.lower()
        
        # Анализируем что есть в контексте
        has_route = any(word in context_lower for word in ['из', 'от', 'до', 'в', 'москва', 'спб', 'питер', 'екатеринбург'])
        has_cargo = any(word in context_lower for word in ['кг', 'тонн', 'груз', 'мебель', 'коробки', 'авто'])
        has_greeting = any(word in context_lower for word in ['привет', 'здравствуйте', 'добрый'])
        
        # Логика ответов
        if 'рассчитываю стоимость' in context_lower:
            return {
                "response": "Понял, ожидайте расчет",
                "needs_price_calculation": False,
                "has_all_info": True
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
