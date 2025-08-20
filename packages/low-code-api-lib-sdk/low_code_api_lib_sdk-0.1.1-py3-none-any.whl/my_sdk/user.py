from .base import BaseModule
from .exceptions import ValidationError, NotFoundError

class User(BaseModule):
    """Модуль для работы с пользователями"""
    
    def get_info(self, user_id=None):
        """Получение информации о пользователе
        
        Args:
            user_id (int, optional): ID пользователя. Если не указан, возвращает информацию о текущем пользователе
            
        Returns:
            dict: Информация о пользователе
            
        Raises:
            ValidationError: Если user_id невалиден
            NotFoundError: Если пользователь не найден
        """
        if user_id is not None:
            self._validate_id(user_id, "user_id")
            return self.client.get(f"/api/user/{user_id}")
        return self.client.get("/api/user/info")
    
    def get_stats(self, user_id=None):
        """Получение статистики пользователя
        
        Args:
            user_id (int, optional): ID пользователя. Если не указан, возвращает статистику текущего пользователя
            
        Returns:
            dict: Статистика пользователя
            
        Raises:
            ValidationError: Если user_id невалиден
            NotFoundError: Если пользователь не найден
        """
        if user_id is not None:
            self._validate_id(user_id, "user_id")
            return self.client.get(f"/api/user/{user_id}/stats")
        return self.client.get("/api/user/stats")
    
    def get_users(self, limit=None, offset=None):
        """Получение списка пользователей
        
        Args:
            limit (int, optional): Максимальное количество пользователей
            offset (int, optional): Смещение для пагинации
            
        Returns:
            dict: Список пользователей
            
        Raises:
            ValidationError: Если параметры невалидны
        """
        params = {}
        if limit is not None:
            if not isinstance(limit, int) or limit <= 0:
                raise ValidationError("limit должен быть положительным целым числом")
            params['limit'] = limit
        if offset is not None:
            if not isinstance(offset, int) or offset < 0:
                raise ValidationError("offset должен быть неотрицательным целым числом")
            params['offset'] = offset
            
        return self.client.get("/api/users", params=params)
    
    def create_user(self, user_data):
        """Создание нового пользователя
        
        Args:
            user_data (dict): Данные пользователя
            
        Returns:
            dict: Созданный пользователь
            
        Raises:
            ValidationError: Если данные пользователя невалидны
        """
        required_fields = ['name', 'email']
        self._validate_required_params(user_data, required_fields)
        
        if not isinstance(user_data.get('email'), str) or '@' not in user_data['email']:
            raise ValidationError("email должен быть валидным email адресом")
            
        return self.client.post("/api/users", json=user_data)
    
    def update_user(self, user_id, user_data):
        """Обновление пользователя
        
        Args:
            user_id (int): ID пользователя
            user_data (dict): Данные для обновления
            
        Returns:
            dict: Обновленный пользователь
            
        Raises:
            ValidationError: Если параметры невалидны
            NotFoundError: Если пользователь не найден
        """
        self._validate_id(user_id, "user_id")
        
        if not isinstance(user_data, dict) or not user_data:
            raise ValidationError("user_data должен быть непустым словарем")
            
        if 'email' in user_data and (not isinstance(user_data['email'], str) or '@' not in user_data['email']):
            raise ValidationError("email должен быть валидным email адресом")
            
        return self.client.put(f"/api/users/{user_id}", json=user_data)
    
    def delete_user(self, user_id):
        """Удаление пользователя
        
        Args:
            user_id (int): ID пользователя
            
        Returns:
            dict: Результат удаления
            
        Raises:
            ValidationError: Если user_id невалиден
            NotFoundError: Если пользователь не найден
        """
        self._validate_id(user_id, "user_id")
        return self.client.delete(f"/api/users/{user_id}")