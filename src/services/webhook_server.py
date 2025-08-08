from flask import Flask, request, jsonify
import json
import logging
import psycopg2

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('webhook_server')

class WebhookHandler:
    def __init__(self):
        self.db_config = {
            'host': "89.169.45.152",
            'database': "Avito",
            'user': "Tim",
            'password': "AVITOPassw0rd"
        }
    
    def process_webhook(self, data):
        logger.info(f"Webhook received: {json.dumps(data, ensure_ascii=False)}")
        
        self.save_webhook_event(data)
        
        # Проверяем новый формат webhook от Avito
        if 'payload' in data and data['payload'].get('type') == 'message':
            message_data = data['payload']['value']
            
            # Проверяем что это входящее сообщение от клиента
            if message_data.get('content', {}).get('text'):
                logger.info(f"Processing new message: {message_data['content']['text']}")
                self.save_new_message(message_data)
        
        return True
    
    def save_webhook_event(self, data):
        try:
            conn = psycopg2.connect(**self.db_config)
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO avito_webhook_events (event_data, processed)
                    VALUES (%s, %s)
                """, (json.dumps(data, ensure_ascii=False), False))
                conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Save webhook error: {e}")
    
    def save_new_message(self, message_data):
        try:
            from .message_accumulator import message_accumulator

            if message_data.get('author_id') == 414329950:
                logger.info(f"Skipping our own message: {message_data['content']['text'][:30]}...")
                return
            
            conn = psycopg2.connect(**self.db_config)
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO simple_messages 
                    (message_id, chat_id, author_id, created, direction, content_text, ai_processed)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (message_id) DO NOTHING
                """, (
                    message_data['id'],
                    message_data['chat_id'],
                    message_data.get('author_id', 0),
                    message_data.get('created', 0),
                    'in',  # �������� ���������
                    message_data['content']['text'],
                    False
                ))

                if cursor.rowcount > 0:
                    logger.info(f"New message saved: {message_data['content']['text'][:50]}...")
                    conn.commit()

                    message_accumulator.add_message(message_data['chat_id'])
                else:
                    logger.info("Message already exists")
                    
            conn.close()
            
        except Exception as e:
            logger.error(f"Save message error: {e}")

webhook_handler = WebhookHandler()

@app.route('/avito/webhook', methods=['POST'])
def avito_webhook():
    try:
        data = request.get_json()
        webhook_handler.process_webhook(data)
        return jsonify({'status': 'ok'}), 200
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
