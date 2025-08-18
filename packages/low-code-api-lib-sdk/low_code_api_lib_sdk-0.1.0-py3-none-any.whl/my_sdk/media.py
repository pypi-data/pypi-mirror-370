from .base import BaseModule

class Media(BaseModule):
    """Модуль для работы с медиафайлами"""
    
    def upload_media(self, bot_id, file_data, **kwargs):
        """Загрузка медиафайлов для бота
        
        Args:
            bot_id: ID бота
            file_data: Данные файла или путь к файлу
            **kwargs: Дополнительные параметры
            
        Returns:
            dict: Результат запроса
        """
        data = {"file": file_data, **kwargs}
        return self.client.post(f"/upload_media/{bot_id}", data)