#!/usr/bin/env python3

import redis
import pika
import psycopg2
import psycopg2.extras

def test_postgresql():
    """Тест подключения к PostgreSQL"""
    print("🔍 Тестируем PostgreSQL...")
    try:
        connection = psycopg2.connect(
            host="89.169.45.152",
            port=5432,
            database="Avito",
            user="Tim",
            password="AVITOPassw0rd",
            cursor_factory=psycopg2.extras.RealDictCursor
        )
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            result = cursor.fetchone()
            print(f"✅ PostgreSQL работает: {result['version'][:50]}...")
        
        connection.close()
        return True
    except Exception as e:
        print(f"❌ PostgreSQL ошибка: {e}")
        return False

def test_redis():
    """Тест подключения к Redis"""
    print("🔍 Тестируем Redis...")
    try:
        r = redis.Redis(
            host="31.130.151.91",
            port=6379,
            username="Tim",
            password="AVITOPassw0rd",
            decode_responses=True
        )
        r.ping()
        info = r.info()
        print(f"✅ Redis работает: версия {info['redis_version']}")
        return True
    except Exception as e:
        print(f"❌ Redis ошибка: {e}")
        return False

def test_rabbitmq():
    """Тест подключения к RabbitMQ"""
    print("🔍 Тестируем RabbitMQ...")
    try:
        uri = 'amqp://Tim:AVITOPassw0rd@85.193.95.165:5672/Avito'
        connection = pika.BlockingConnection(pika.URLParameters(uri))
        channel = connection.channel()
        print("✅ RabbitMQ работает")
        connection.close()
        return True
    except Exception as e:
        print(f"❌ RabbitMQ ошибка: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Тестирование подключений к сервисам\n")
    
    results = []
    results.append(test_postgresql())
    results.append(test_redis())
    results.append(test_rabbitmq())
    
    print(f"\n📊 Результат: {sum(results)}/3 сервисов работают")
    
    if all(results):
        print("🎉 Все сервисы настроены корректно!")
    else:
        print("⚠️ Есть проблемы с подключениями")
