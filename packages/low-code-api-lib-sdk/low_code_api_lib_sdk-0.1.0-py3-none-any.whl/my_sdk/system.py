from .base import BaseModule

class System(BaseModule):
    """Модуль для работы с системными функциями"""
    
    def health_check(self):
        """Проверка работоспособности системы
        
        Returns:
            dict: Результат запроса
        """
        return self.client.get("/health")