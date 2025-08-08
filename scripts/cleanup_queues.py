#!/usr/bin/env python3

import pika

def cleanup_queues():
    """Удаление всех очередей для пересоздания"""
    try:
        print("🧹 Очищаем существующие очереди...")
        
        uri = 'amqp://Tim:AVITOPassw0rd@85.193.95.165:5672/Avito'
        connection = pika.BlockingConnection(pika.URLParameters(uri))
        channel = connection.channel()
        
        queues_to_delete = [
            'avito.messages.incoming',
            'avito.ai.processing', 
            'avito.messages.outgoing',
            'avito.price.calculate',
            'avito.admin.notifications',
            'avito.amocrm.sync'
        ]
        
        for queue_name in queues_to_delete:
            try:
                channel.queue_delete(queue=queue_name)
                print(f"  ✅ Удалена очередь: {queue_name}")
            except Exception as e:
                print(f"  ⚠️ Очередь {queue_name} не найдена или уже удалена")
        
        # Пересоздаем очереди без TTL
        print("\n🔨 Создаем очереди заново...")
        for queue_name in queues_to_delete:
            channel.queue_declare(queue=queue_name, durable=True)
            print(f"  ✅ Создана очередь: {queue_name}")
        
        connection.close()
        print("\n🎉 Все очереди пересозданы успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка очистки очередей: {e}")
        return False

if __name__ == "__main__":
    cleanup_queues()
