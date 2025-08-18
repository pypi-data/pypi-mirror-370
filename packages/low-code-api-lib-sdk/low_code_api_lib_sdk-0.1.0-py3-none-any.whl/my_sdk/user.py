from .base import BaseModule

class User(BaseModule):
    """Модуль для работы с пользователями"""
    
    def get_info(self):
        """Получение информации о пользователе
        
        Returns:
            dict: Информация о пользователе
        """
        return self.client.get("/api/user/info")
    
    def get_stats(self):
        """Получение статистики пользователя
        
        Returns:
            dict: Статистика пользователя
        """
        return self.client.get("/api/user/stats")