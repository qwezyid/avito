#!/usr/bin/env python3

import psycopg2

def create_simple_tables():
    conn = psycopg2.connect(
        host="89.169.45.152",
        database="Avito",
        user="Tim",
        password="AVITOPassw0rd"
    )
    
    with conn.cursor() as cursor:
        # Создаем простые таблицы без внешних ключей
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS simple_chats (
                chat_id VARCHAR(255) PRIMARY KEY,
                created BIGINT,
                updated BIGINT,
                status VARCHAR(50) DEFAULT 'active',
                ai_stage VARCHAR(100) DEFAULT 'greeting',
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS simple_messages (
                message_id VARCHAR(255) PRIMARY KEY,
                chat_id VARCHAR(255),
                author_id BIGINT,
                created BIGINT,
                direction VARCHAR(10),
                message_type VARCHAR(50),
                content_text TEXT,
                ai_processed BOOLEAN DEFAULT FALSE,
                processed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        conn.commit()
        print("✅ Simple tables created")
    
    conn.close()

if __name__ == "__main__":
    create_simple_tables()
