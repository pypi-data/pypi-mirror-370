from .base import BaseModule
from .exceptions import ValidationError, AuthenticationError

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
    
    def manage_user(self, user_id, action, **kwargs):
        """Управление пользователем
        
        Args:
            user_id: ID пользователя
            action: Действие (ban, unban, delete, activate, deactivate)
            **kwargs: Дополнительные параметры
            
        Returns:
            dict: Результат запроса
        """
        self._validate_id(user_id, "user_id")
        
        valid_actions = ['ban', 'unban', 'delete', 'activate', 'deactivate']
        if action not in valid_actions:
            raise ValidationError(f"Action must be one of: {', '.join(valid_actions)}")
            
        data = {"action": action, **kwargs}
        return self.client.post(f"/api/admin/user/{user_id}/manage", json=data)
    
    def get_users(self, limit=50, offset=0, status=None, **kwargs):
        """Получение списка пользователей для администратора
        
        Args:
            limit: Максимальное количество пользователей (по умолчанию 50)
            offset: Смещение для пагинации (по умолчанию 0)
            status: Статус пользователей (active, banned, deleted)
            **kwargs: Дополнительные параметры
            
        Returns:
            dict: Список пользователей
        """
        if not isinstance(limit, int) or limit <= 0 or limit > 100:
            raise ValidationError("Limit must be a positive integer not exceeding 100")
            
        if not isinstance(offset, int) or offset < 0:
            raise ValidationError("Offset must be a non-negative integer")
            
        params = {"limit": limit, "offset": offset, **kwargs}
        if status:
            valid_statuses = ['active', 'banned', 'deleted']
            if status not in valid_statuses:
                raise ValidationError(f"Status must be one of: {', '.join(valid_statuses)}")
            params["status"] = status
            
        return self.client.get("/api/admin/users", params=params)
    
    def get_system_logs(self, limit=100, offset=0, level=None, **kwargs):
        """Получение системных логов
        
        Args:
            limit: Максимальное количество записей (по умолчанию 100)
            offset: Смещение для пагинации (по умолчанию 0)
            level: Уровень логов (error, warning, info, debug)
            **kwargs: Дополнительные параметры
            
        Returns:
            dict: Системные логи
        """
        if not isinstance(limit, int) or limit <= 0 or limit > 1000:
            raise ValidationError("Limit must be a positive integer not exceeding 1000")
            
        if not isinstance(offset, int) or offset < 0:
            raise ValidationError("Offset must be a non-negative integer")
            
        params = {"limit": limit, "offset": offset, **kwargs}
        if level:
            valid_levels = ['error', 'warning', 'info', 'debug']
            if level not in valid_levels:
                raise ValidationError(f"Level must be one of: {', '.join(valid_levels)}")
            params["level"] = level
            
        return self.client.get("/api/admin/logs", params=params)
    
    def update_system_config(self, config_data):
        """Обновление системной конфигурации
        
        Args:
            config_data: Данные конфигурации
            
        Returns:
            dict: Результат запроса
        """
        if not config_data or not isinstance(config_data, dict):
            raise ValidationError("Config data must be a non-empty dictionary")
            
        return self.client.put("/api/admin/config", json=config_data)
    
    def get_system_config(self):
        """Получение системной конфигурации
        
        Returns:
            dict: Системная конфигурация
        """
        return self.client.get("/api/admin/config")