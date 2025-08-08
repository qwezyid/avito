import requests
import logging
import psycopg2
import psycopg2.extras
from typing import Optional, Dict, List
from datetime import datetime

logger = logging.getLogger('avito_client')

class AvitoClient:
    def __init__(self):
        self.base_url = "https://api.avito.ru"
        self.db_config = {
            'host': "89.169.45.152",
            'database': "Avito",
            'user': "Tim",
            'password': "AVITOPassw0rd"
        }
    
    def get_active_token(self) -> Optional[str]:
        try:
            conn = psycopg2.connect(**self.db_config)
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT access_token FROM avito_auth_tokens 
                    WHERE is_active = TRUE AND expires_at > NOW()
                    ORDER BY created_at DESC LIMIT 1
                """)
                result = cursor.fetchone()
                conn.close()
                return result[0] if result else None
        except Exception as e:
            logger.error(f"Token fetch error: {e}")
            return None
    
    def make_request(self, method: str, endpoint: str, **kwargs) -> Optional[requests.Response]:
        token = self.get_active_token()
        if not token:
            logger.error("No active token available")
            return None
        
        headers = kwargs.get('headers', {})
        headers['Authorization'] = f'Bearer {token}'
        kwargs['headers'] = headers
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.request(method, url, **kwargs)
            return response
        except Exception as e:
            logger.error(f"API request error: {e}")
            return None
    
    def get_chats(self, user_id: int, **params) -> Optional[List[Dict]]:
        endpoint = f"/messenger/v2/accounts/{user_id}/chats"
        response = self.make_request('GET', endpoint, params=params)
        
        if response and response.status_code == 200:
            data = response.json()
            return data.get('chats', [])
        else:
            logger.error(f"Get chats failed: {response.status_code if response else 'No response'}")
            return None
    
    def get_messages(self, user_id: int, chat_id: str, **params) -> Optional[List[Dict]]:
        endpoint = f"/messenger/v3/accounts/{user_id}/chats/{chat_id}/messages/"
        response = self.make_request('GET', endpoint, params=params)
        
        if response and response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'messages' in data:
                return data['messages']
            else:
                logger.info(f"Raw message response: {data}")
                return []
        else:
            logger.error(f"Get messages failed: {response.status_code if response else 'No response'}")
            return None

    def mark_chat_read(self, user_id: int, chat_id: str) -> bool:
        endpoint = f"/messenger/v1/accounts/{user_id}/chats/{chat_id}/read"
        response = self.make_request('POST', endpoint)
        
        if response and response.status_code == 200:
            return True
        else:
            logger.error(f"Mark read failed: {response.status_code if response else 'No response'}")
            return False    
    def send_message(self, user_id: int, chat_id: str, text: str) -> Optional[Dict]:
        endpoint = f"/messenger/v1/accounts/{user_id}/chats/{chat_id}/messages"
        data = {
            "message": {"text": text},
            "type": "text"
        }
        
        response = self.make_request('POST', endpoint, json=data)
        
        if response and response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Send message failed: {response.status_code if response else 'No response'}")
            return None

avito_client = AvitoClient()
