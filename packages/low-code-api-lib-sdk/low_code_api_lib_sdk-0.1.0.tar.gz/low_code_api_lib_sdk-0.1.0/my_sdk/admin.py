from .base import BaseModule

class Admin(BaseModule):
    """Модуль для работы с административными функциями"""
    
    def get_stats(self):
        """Получение статистики для администратора
        
        Returns:
            dict: Результат запроса
        """
        return self.client.get("/api/admin/stats")
    
    def get_comprehensive_stats(self):
        """Получение комплексной статистики платформы
        
        Returns:
            dict: Результат запроса
        """
        return self.client.get("/api/admin/comprehensive-stats")