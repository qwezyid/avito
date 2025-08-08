import psycopg2
import psycopg2.extras
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.connection = None
        
    def connect(self):
        """Подключение к PostgreSQL"""
        try:
            self.connection = psycopg2.connect(
                host="89.169.45.152",
                port=5432,
                database="Avito",
                user="Tim",
                password="AVITOPassw0rd",
                cursor_factory=psycopg2.extras.RealDictCursor
            )
            logger.info("Успешное подключение к PostgreSQL")
            return True
        except Exception as e:
            logger.error(f"Ошибка подключения к PostgreSQL: {e}")
            return False
    
    def execute_query(self, query, params=None):
        """Выполнение SQL запроса"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                if query.strip().upper().startswith('SELECT'):
                    return cursor.fetchall()
                self.connection.commit()
                return cursor.rowcount
        except Exception as e:
            logger.error(f"Ошибка выполнения запроса: {e}")
            self.connection.rollback()
            return None
    
    def close(self):
        """Закрытие подключения"""
        if self.connection:
            self.connection.close()
            logger.info("Подключение к PostgreSQL закрыто")

# Глобальный экземпляр
db_manager = DatabaseManager()
