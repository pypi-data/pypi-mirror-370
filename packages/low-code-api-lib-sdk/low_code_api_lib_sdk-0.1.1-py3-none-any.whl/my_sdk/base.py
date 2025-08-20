from .exceptions import ValidationError


class BaseModule:
    """Базовый класс для всех модулей API с расширенной функциональностью."""
    
    def __init__(self, client):
        """Инициализация модуля с клиентом API
        
        Args:
            client: Экземпляр класса Client для выполнения запросов к API
        """
        if client is None:
            raise ValidationError("Client не может быть None")
        
        self.client = client
    
    def _validate_required_params(self, params, required_fields):
        """Валидация обязательных параметров.
        
        Args:
            params: Словарь параметров
            required_fields: Список обязательных полей
            
        Raises:
            ValidationError: Если отсутствуют обязательные параметры
        """
        missing_fields = []
        for field in required_fields:
            if field not in params or params[field] is None:
                missing_fields.append(field)
        
        if missing_fields:
            raise ValidationError(f"Отсутствуют обязательные параметры: {', '.join(missing_fields)}")
    
    def _validate_id(self, id_value, field_name="id"):
        """Валидация ID параметра.
        
        Args:
            id_value: Значение ID
            field_name: Название поля для ошибки
            
        Raises:
            ValidationError: Если ID невалидный
        """
        if not isinstance(id_value, (int, str)) or (isinstance(id_value, str) and not id_value.strip()):
            raise ValidationError(f"{field_name} должен быть непустой строкой или числом")
        
        if isinstance(id_value, int) and id_value <= 0:
            raise ValidationError(f"{field_name} должен быть положительным числом")
    
    def __repr__(self):
        """Строковое представление модуля."""
        return f"{self.__class__.__name__}(client={self.client.__class__.__name__})"