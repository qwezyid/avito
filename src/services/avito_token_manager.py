import requests
import psycopg2
import psycopg2.extras
import logging
import schedule
import time
import threading
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger('avito_token_manager')

class AvitoTokenManager:
    def __init__(self):
        self.client_id = "YeC-TGQyeGBvxYDWN5SX"
        self.client_secret = "k7O3scz-0cX4JpKnkq7fOBmcOMHJdl6sPZiTMaBY"
        self.token_url = "https://api.avito.ru/token"
        self.db_config = {
            'host': "89.169.45.152",
            'database': "Avito",
            'user': "Tim",
            'password': "AVITOPassw0rd"
        }
        self.running = False
        
    def get_token(self) -> Optional[dict]:
        try:
            response = requests.post(
                self.token_url,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                data={
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'grant_type': 'client_credentials'
                },
                timeout=30
            )
            
            logger.info(f"Token response status: {response.status_code}")
            logger.info(f"Token response body: {response.text}")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Token request failed: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Token request error: {e}")
            return None
    
    def save_token(self, token_data: dict) -> bool:
        if not token_data or 'access_token' not in token_data:
            logger.error(f"Invalid token data: {token_data}")
            return False
            
        try:
            conn = psycopg2.connect(**self.db_config)
            with conn.cursor() as cursor:
                cursor.execute("UPDATE avito_auth_tokens SET is_active = FALSE")
                
                expires_at = datetime.now() + timedelta(seconds=token_data['expires_in'] - 3600)
                
                cursor.execute("""
                    INSERT INTO avito_auth_tokens (access_token, token_type, expires_in, expires_at, client_id, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    token_data['access_token'],
                    token_data.get('token_type', 'Bearer'),
                    token_data['expires_in'],
                    expires_at,
                    self.client_id,
                    True
                ))
                
                conn.commit()
            conn.close()
            logger.info(f"Token saved successfully, expires at: {expires_at}")
            return True
        except Exception as e:
            logger.error(f"Database error: {e}")
            return False    
            
    def refresh_token(self):
        logger.info("Refreshing token...")
        token_data = self.get_token()
        if token_data:
            if self.save_token(token_data):
                logger.info("Token refreshed successfully")
            else:
                logger.error("Failed to save token")
        else:
            logger.error("Failed to get new token")
    
    def start_scheduler(self):
        if self.running:
            return
            
        schedule.every().day.at("23:59").do(self.refresh_token)
        
        def run():
            self.running = True
            logger.info("Token scheduler started (daily at 23:59)")
            while self.running:
                schedule.run_pending()
                time.sleep(60)
        
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        
        self.refresh_token()
    
    def stop_scheduler(self):
        self.running = False

token_manager = AvitoTokenManager()
