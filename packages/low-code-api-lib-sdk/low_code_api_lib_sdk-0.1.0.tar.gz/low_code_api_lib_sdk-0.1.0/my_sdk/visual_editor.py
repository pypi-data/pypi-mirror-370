from .base import BaseModule

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
        data = {"bot_data": bot_data, **kwargs}
        return self.client.post("/api/save-visual-bot", data)
    
    def generate_code(self, blocks, **kwargs):
        """Генерация кода из блоков
        
        Args:
            blocks: Блоки кода
            **kwargs: Дополнительные параметры
            
        Returns:
            dict: Результат запроса
        """
        data = {"blocks": blocks, **kwargs}
        return self.client.post("/api/generate-code", data)
    
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
        data = {"blocks": blocks, **kwargs}
        return self.client.post("/api/validate-blocks", data)
    
    def create_custom_block(self, block_data, **kwargs):
        """Создание пользовательского блока
        
        Args:
            block_data: Данные блока
            **kwargs: Дополнительные параметры
            
        Returns:
            dict: Результат запроса
        """
        data = {"block_data": block_data, **kwargs}
        return self.client.post("/api/custom-block", data)