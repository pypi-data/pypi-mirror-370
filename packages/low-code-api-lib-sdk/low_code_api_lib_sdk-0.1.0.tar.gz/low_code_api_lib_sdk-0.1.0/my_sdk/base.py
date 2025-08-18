class BaseModule:
    """Базовый класс для всех модулей API"""
    
    def __init__(self, client):
        """Инициализация модуля с клиентом API
        
        Args:
            client: Экземпляр класса Client для выполнения запросов к API
        """
        self.client = client