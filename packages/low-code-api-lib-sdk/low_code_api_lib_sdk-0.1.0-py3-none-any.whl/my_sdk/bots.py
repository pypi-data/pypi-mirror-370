from .base import BaseModule

class Bots(BaseModule):
    """Модуль для работы с ботами"""
    
    def generate_code(self, bot_id, **kwargs):
        """Генерация кода бота
        
        Args:
            bot_id: ID бота
            **kwargs: Дополнительные параметры
            
        Returns:
            dict: Результат запроса
        """
        return self.client.post(f"/generate_code/{bot_id}", kwargs)
    
    def run_bot(self, bot_id, **kwargs):
        """Запуск бота
        
        Args:
            bot_id: ID бота
            **kwargs: Дополнительные параметры
            
        Returns:
            dict: Результат запроса
        """
        return self.client.post(f"/run_bot/{bot_id}", kwargs)
    
    def stop_bot(self, bot_id, **kwargs):
        """Остановка бота
        
        Args:
            bot_id: ID бота
            **kwargs: Дополнительные параметры
            
        Returns:
            dict: Результат запроса
        """
        return self.client.post(f"/stop_bot/{bot_id}", kwargs)
    
    def get_bot_status(self, bot_id):
        """Получение статуса бота
        
        Args:
            bot_id: ID бота
            
        Returns:
            dict: Результат запроса
        """
        return self.client.get(f"/get_bot_status/{bot_id}")
    
    def add_command(self, bot_id, **kwargs):
        """Добавление команды боту
        
        Args:
            bot_id: ID бота
            **kwargs: Параметры команды
            
        Returns:
            dict: Результат запроса
        """
        return self.client.post(f"/add_command/{bot_id}", kwargs)
    
    def add_handler(self, bot_id, **kwargs):
        """Добавление обработчика боту
        
        Args:
            bot_id: ID бота
            **kwargs: Параметры обработчика
            
        Returns:
            dict: Результат запроса
        """
        return self.client.post(f"/add_handler/{bot_id}", kwargs)
    
    def delete_command(self, command_id):
        """Удаление команды бота
        
        Args:
            command_id: ID команды
            
        Returns:
            dict: Результат запроса
        """
        return self.client.post(f"/delete_command/{command_id}")
    
    def delete_handler(self, handler_id):
        """Удаление обработчика бота
        
        Args:
            handler_id: ID обработчика
            
        Returns:
            dict: Результат запроса
        """
        return self.client.post(f"/delete_handler/{handler_id}")
    
    def delete_bot(self, bot_id):
        """Удаление бота
        
        Args:
            bot_id: ID бота
            
        Returns:
            dict: Результат запроса
        """
        return self.client.post(f"/delete_bot/{bot_id}")
    
    def get_command(self, command_id):
        """Получение информации о команде
        
        Args:
            command_id: ID команды
            
        Returns:
            dict: Результат запроса
        """
        return self.client.get(f"/get_command/{command_id}")
    
    def edit_command(self, command_id, **kwargs):
        """Редактирование команды
        
        Args:
            command_id: ID команды
            **kwargs: Новые параметры команды
            
        Returns:
            dict: Результат запроса
        """
        return self.client.post(f"/edit_command/{command_id}", kwargs)
    
    def download_zip_bot(self, bot_id):
        """Скачивание бота в ZIP-архиве
        
        Args:
            bot_id: ID бота
            
        Returns:
            dict: Результат запроса
        """
        return self.client.get(f"/download_zip_bot/{bot_id}")