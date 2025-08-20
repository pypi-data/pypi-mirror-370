from .base import BaseModule
from .exceptions import ValidationError

class System(BaseModule):
    """Модуль для работы с системными функциями"""
    
    def health_check(self):
        """Проверка работоспособности системы
        
        Returns:
            dict: Результат запроса
        """
        return self.client.get("/health")
    
    def get_version(self):
        """Получение версии системы
        
        Returns:
            dict: Информация о версии
        """
        return self.client.get("/version")
    
    def get_system_info(self):
        """Получение информации о системе
        
        Returns:
            dict: Системная информация
        """
        return self.client.get("/system/info")
    
    def get_api_limits(self):
        """Получение лимитов API
        
        Returns:
            dict: Лимиты API
        """
        return self.client.get("/system/limits")
    
    def ping(self):
        """Ping сервера
        
        Returns:
            dict: Результат ping
        """
        return self.client.get("/ping")
    
    def get_server_time(self):
        """Получение времени сервера
        
        Returns:
            dict: Время сервера
        """
        return self.client.get("/system/time")
    
    def validate_token(self, token=None):
        """Валидация токена
        
        Args:
            token: Токен для валидации (опционально, по умолчанию текущий)
            
        Returns:
            dict: Результат валидации
        """
        data = {}
        if token:
            if not isinstance(token, str) or not token.strip():
                raise ValidationError("Token must be a non-empty string")
            data["token"] = token.strip()
            
        return self.client.post("/system/validate-token", json=data)
    
    def get_supported_features(self):
        """Получение списка поддерживаемых функций
        
        Returns:
            dict: Список поддерживаемых функций
        """
        return self.client.get("/system/features")