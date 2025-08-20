from .base import BaseModule
from .exceptions import ValidationError, NotFoundError

class Bots(BaseModule):
    """Модуль для работы с ботами"""
    
    def generate_code(self, bot_id, **kwargs):
        """Генерация кода бота
        
        Args:
            bot_id (int): ID бота
            **kwargs: Дополнительные параметры
            
        Returns:
            dict: Результат запроса
            
        Raises:
            ValidationError: Если bot_id невалиден
            NotFoundError: Если бот не найден
        """
        self._validate_id(bot_id, "bot_id")
        return self.client.post(f"/generate_code/{bot_id}", json=kwargs)
    
    def run_bot(self, bot_id, **kwargs):
        """Запуск бота
        
        Args:
            bot_id (int): ID бота
            **kwargs: Дополнительные параметры
            
        Returns:
            dict: Результат запроса
            
        Raises:
            ValidationError: Если bot_id невалиден
            NotFoundError: Если бот не найден
        """
        self._validate_id(bot_id, "bot_id")
        return self.client.post(f"/run_bot/{bot_id}", json=kwargs)
    
    def stop_bot(self, bot_id, **kwargs):
        """Остановка бота
        
        Args:
            bot_id (int): ID бота
            **kwargs: Дополнительные параметры
            
        Returns:
            dict: Результат запроса
            
        Raises:
            ValidationError: Если bot_id невалиден
            NotFoundError: Если бот не найден
        """
        self._validate_id(bot_id, "bot_id")
        return self.client.post(f"/stop_bot/{bot_id}", json=kwargs)
    
    def get_bot_status(self, bot_id):
        """Получение статуса бота
        
        Args:
            bot_id (int): ID бота
            
        Returns:
            dict: Результат запроса
            
        Raises:
            ValidationError: Если bot_id невалиден
            NotFoundError: Если бот не найден
        """
        self._validate_id(bot_id, "bot_id")
        return self.client.get(f"/get_bot_status/{bot_id}")
    
    def add_command(self, bot_id, command_name, **kwargs):
        """Добавление команды боту
        
        Args:
            bot_id (int): ID бота
            command_name (str): Название команды
            **kwargs: Параметры команды
            
        Returns:
            dict: Результат запроса
            
        Raises:
            ValidationError: Если параметры невалидны
            NotFoundError: Если бот не найден
        """
        self._validate_id(bot_id, "bot_id")
        if not isinstance(command_name, str) or not command_name.strip():
            raise ValidationError("command_name должен быть непустой строкой")
        
        data = {'command_name': command_name, **kwargs}
        return self.client.post(f"/add_command/{bot_id}", json=data)
    
    def add_handler(self, bot_id, handler_type, **kwargs):
        """Добавление обработчика боту
        
        Args:
            bot_id (int): ID бота
            handler_type (str): Тип обработчика
            **kwargs: Параметры обработчика
            
        Returns:
            dict: Результат запроса
            
        Raises:
            ValidationError: Если параметры невалидны
            NotFoundError: Если бот не найден
        """
        self._validate_id(bot_id, "bot_id")
        if not isinstance(handler_type, str) or not handler_type.strip():
            raise ValidationError("handler_type должен быть непустой строкой")
        
        data = {'handler_type': handler_type, **kwargs}
        return self.client.post(f"/add_handler/{bot_id}", json=data)
    
    def delete_command(self, command_id):
        """Удаление команды бота
        
        Args:
            command_id (int): ID команды
            
        Returns:
            dict: Результат запроса
            
        Raises:
            ValidationError: Если command_id невалиден
            NotFoundError: Если команда не найдена
        """
        self._validate_id(command_id, "command_id")
        return self.client.delete(f"/delete_command/{command_id}")
    
    def delete_handler(self, handler_id):
        """Удаление обработчика бота
        
        Args:
            handler_id (int): ID обработчика
            
        Returns:
            dict: Результат запроса
            
        Raises:
            ValidationError: Если handler_id невалиден
            NotFoundError: Если обработчик не найден
        """
        self._validate_id(handler_id, "handler_id")
        return self.client.delete(f"/delete_handler/{handler_id}")
    
    def delete_bot(self, bot_id):
        """Удаление бота
        
        Args:
            bot_id (int): ID бота
            
        Returns:
            dict: Результат запроса
            
        Raises:
            ValidationError: Если bot_id невалиден
            NotFoundError: Если бот не найден
        """
        self._validate_id(bot_id, "bot_id")
        return self.client.delete(f"/delete_bot/{bot_id}")
    
    def get_command(self, command_id):
        """Получение информации о команде
        
        Args:
            command_id (int): ID команды
            
        Returns:
            dict: Результат запроса
            
        Raises:
            ValidationError: Если command_id невалиден
            NotFoundError: Если команда не найдена
        """
        self._validate_id(command_id, "command_id")
        return self.client.get(f"/get_command/{command_id}")
    
    def edit_command(self, command_id, **kwargs):
        """Редактирование команды
        
        Args:
            command_id (int): ID команды
            **kwargs: Новые параметры команды
            
        Returns:
            dict: Результат запроса
            
        Raises:
            ValidationError: Если command_id невалиден или данные пусты
            NotFoundError: Если команда не найдена
        """
        self._validate_id(command_id, "command_id")
        if not kwargs:
            raise ValidationError("Необходимо указать хотя бы один параметр для обновления")
        return self.client.put(f"/edit_command/{command_id}", json=kwargs)
    
    def download_zip_bot(self, bot_id):
        """Скачивание бота в ZIP-архиве
        
        Args:
            bot_id (int): ID бота
            
        Returns:
            dict: Результат запроса
            
        Raises:
            ValidationError: Если bot_id невалиден
            NotFoundError: Если бот не найден
        """
        self._validate_id(bot_id, "bot_id")
        return self.client.get(f"/download_zip_bot/{bot_id}")