from .base import BaseModule
from .exceptions import ValidationError

class VisualEditor(BaseModule):
    """Модуль для работы с визуальным редактором"""
    
    def save_visual_bot(self, bot_data, **kwargs):
        """Сохранение бота из визуального редактора
        
        Args:
            bot_data: Данные бота
            **kwargs: Дополнительные параметры
            
        Returns:
            dict: Результат запроса
        """
        if not bot_data or not isinstance(bot_data, dict):
            raise ValidationError("Bot data must be a non-empty dictionary")
            
        data = {"bot_data": bot_data, **kwargs}
        return self.client.post("/api/save-visual-bot", json=data)
    
    def generate_code(self, blocks, **kwargs):
        """Генерация кода из блоков
        
        Args:
            blocks: Блоки кода
            **kwargs: Дополнительные параметры
            
        Returns:
            dict: Результат запроса
        """
        if not blocks or not isinstance(blocks, (list, dict)):
            raise ValidationError("Blocks must be a non-empty list or dictionary")
            
        data = {"blocks": blocks, **kwargs}
        return self.client.post("/api/generate-code", json=data)
    
    def get_blocks_config(self):
        """Получение конфигурации блоков
        
        Returns:
            dict: Результат запроса
        """
        return self.client.get("/api/blocks-config")
    
    def validate_blocks(self, blocks, **kwargs):
        """Валидация блоков
        
        Args:
            blocks: Блоки кода
            **kwargs: Дополнительные параметры
            
        Returns:
            dict: Результат запроса
        """
        if not blocks or not isinstance(blocks, (list, dict)):
            raise ValidationError("Blocks must be a non-empty list or dictionary")
            
        data = {"blocks": blocks, **kwargs}
        return self.client.post("/api/validate-blocks", json=data)
    
    def create_custom_block(self, block_data, **kwargs):
        """Создание пользовательского блока
        
        Args:
            block_data: Данные блока
            **kwargs: Дополнительные параметры
            
        Returns:
            dict: Результат запроса
        """
        if not block_data or not isinstance(block_data, dict):
            raise ValidationError("Block data must be a non-empty dictionary")
            
        # Проверяем обязательные поля
        required_fields = ['name', 'type']
        for field in required_fields:
            if field not in block_data or not block_data[field]:
                raise ValidationError(f"Block data must contain '{field}' field")
                
        data = {"block_data": block_data, **kwargs}
        return self.client.post("/api/custom-block", json=data)
    
    def get_custom_blocks(self, limit=50, offset=0):
        """Получение списка пользовательских блоков
        
        Args:
            limit: Максимальное количество блоков (по умолчанию 50)
            offset: Смещение для пагинации (по умолчанию 0)
            
        Returns:
            dict: Список пользовательских блоков
        """
        if not isinstance(limit, int) or limit <= 0 or limit > 100:
            raise ValidationError("Limit must be a positive integer not exceeding 100")
            
        if not isinstance(offset, int) or offset < 0:
            raise ValidationError("Offset must be a non-negative integer")
            
        params = {"limit": limit, "offset": offset}
        return self.client.get("/api/custom-blocks", params=params)
    
    def delete_custom_block(self, block_id):
        """Удаление пользовательского блока
        
        Args:
            block_id: ID блока
            
        Returns:
            dict: Результат запроса
        """
        self._validate_id(block_id, "block_id")
        return self.client.delete(f"/api/custom-block/{block_id}")