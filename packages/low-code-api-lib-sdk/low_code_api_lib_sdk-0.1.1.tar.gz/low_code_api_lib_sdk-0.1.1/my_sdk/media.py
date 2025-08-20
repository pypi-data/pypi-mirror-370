from .base import BaseModule
from .exceptions import ValidationError, NotFoundError
import os

class Media(BaseModule):
    """Модуль для работы с медиафайлами"""
    
    def upload_media(self, bot_id, file_data, file_type=None, **kwargs):
        """Загрузка медиафайлов для бота
        
        Args:
            bot_id (int): ID бота
            file_data: Данные файла (bytes) или путь к файлу (str)
            file_type (str, optional): Тип файла (image, video, audio, document)
            **kwargs: Дополнительные параметры
            
        Returns:
            dict: Результат запроса
            
        Raises:
            ValidationError: Если параметры невалидны или файл не найден
            NotFoundError: Если бот не найден
        """
        self._validate_id(bot_id, "bot_id")
        
        if file_data is None:
            raise ValidationError("file_data не может быть None")
        
        # Если передан путь к файлу
        if isinstance(file_data, str):
            if not os.path.exists(file_data):
                raise ValidationError(f"Файл не найден: {file_data}")
            if not os.path.isfile(file_data):
                raise ValidationError(f"Указанный путь не является файлом: {file_data}")
        elif not isinstance(file_data, (bytes, bytearray)):
            raise ValidationError("file_data должен быть строкой (путь к файлу) или bytes")
        
        if file_type and not isinstance(file_type, str):
            raise ValidationError("file_type должен быть строкой")
        
        data = {"file": file_data}
        if file_type:
            data["file_type"] = file_type
        data.update(kwargs)
        
        return self.client.post(f"/upload_media/{bot_id}", files=data)
    
    def get_media(self, media_id):
        """Получение информации о медиафайле
        
        Args:
            media_id (int): ID медиафайла
            
        Returns:
            dict: Информация о медиафайле
            
        Raises:
            ValidationError: Если media_id невалиден
            NotFoundError: Если медиафайл не найден
        """
        self._validate_id(media_id, "media_id")
        return self.client.get(f"/media/{media_id}")
    
    def delete_media(self, media_id):
        """Удаление медиафайла
        
        Args:
            media_id (int): ID медиафайла
            
        Returns:
            dict: Результат удаления
            
        Raises:
            ValidationError: Если media_id невалиден
            NotFoundError: Если медиафайл не найден
        """
        self._validate_id(media_id, "media_id")
        return self.client.delete(f"/media/{media_id}")
    
    def get_bot_media(self, bot_id, limit=None, offset=None):
        """Получение списка медиафайлов бота
        
        Args:
            bot_id (int): ID бота
            limit (int, optional): Максимальное количество файлов
            offset (int, optional): Смещение для пагинации
            
        Returns:
            dict: Список медиафайлов
            
        Raises:
            ValidationError: Если параметры невалидны
            NotFoundError: Если бот не найден
        """
        self._validate_id(bot_id, "bot_id")
        
        params = {}
        if limit is not None:
            if not isinstance(limit, int) or limit <= 0:
                raise ValidationError("limit должен быть положительным целым числом")
            params['limit'] = limit
        if offset is not None:
            if not isinstance(offset, int) or offset < 0:
                raise ValidationError("offset должен быть неотрицательным целым числом")
            params['offset'] = offset
            
        return self.client.get(f"/bot/{bot_id}/media", params=params)