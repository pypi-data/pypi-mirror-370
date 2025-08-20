from .base import BaseModule
from .exceptions import ValidationError, NotFoundError

class Templates(BaseModule):
    """Модуль для работы с шаблонами"""
    
    def download(self, template_id, **kwargs):
        """Скачивание шаблона
        
        Args:
            template_id: ID шаблона
            **kwargs: Дополнительные параметры
            
        Returns:
            dict: Результат запроса
        """
        self._validate_id(template_id, "template_id")
        return self.client.post(f"/template/{template_id}/download", json=kwargs)
    
    def rate(self, template_id, rating, **kwargs):
        """Оценка шаблона
        
        Args:
            template_id: ID шаблона
            rating: Оценка (1-5)
            **kwargs: Дополнительные параметры
            
        Returns:
            dict: Результат запроса
        """
        self._validate_id(template_id, "template_id")
        
        if not isinstance(rating, (int, float)) or not (1 <= rating <= 5):
            raise ValidationError("Rating must be a number between 1 and 5")
            
        data = {"rating": rating, **kwargs}
        return self.client.post(f"/template/{template_id}/rate", json=data)
    
    def comment(self, template_id, comment_text, **kwargs):
        """Добавление комментария к шаблону
        
        Args:
            template_id: ID шаблона
            comment_text: Текст комментария
            **kwargs: Дополнительные параметры
            
        Returns:
            dict: Результат запроса
        """
        self._validate_id(template_id, "template_id")
        
        if not comment_text or not isinstance(comment_text, str) or not comment_text.strip():
            raise ValidationError("Comment text must be a non-empty string")
            
        data = {"comment": comment_text.strip(), **kwargs}
        return self.client.post(f"/template/{template_id}/comment", json=data)
    
    def use_template(self, template_id, **kwargs):
        """Использование шаблона для создания бота
        
        Args:
            template_id: ID шаблона
            **kwargs: Дополнительные параметры
            
        Returns:
            dict: Результат запроса
        """
        self._validate_id(template_id, "template_id")
        return self.client.post(f"/use_template/{template_id}", json=kwargs)
    
    def toggle_favorite(self, template_id, **kwargs):
        """Добавление/удаление шаблона из избранного
        
        Args:
            template_id: ID шаблона
            **kwargs: Дополнительные параметры
            
        Returns:
            dict: Результат запроса
        """
        self._validate_id(template_id, "template_id")
        return self.client.post(f"/templates/favorite/{template_id}", json=kwargs)
    
    def get_templates(self, limit=50, offset=0, category=None, **kwargs):
        """Получение списка шаблонов
        
        Args:
            limit: Максимальное количество шаблонов (по умолчанию 50)
            offset: Смещение для пагинации (по умолчанию 0)
            category: Категория шаблонов (опционально)
            **kwargs: Дополнительные параметры
            
        Returns:
            dict: Список шаблонов
        """
        if not isinstance(limit, int) or limit <= 0 or limit > 100:
            raise ValidationError("Limit must be a positive integer not exceeding 100")
            
        if not isinstance(offset, int) or offset < 0:
            raise ValidationError("Offset must be a non-negative integer")
            
        params = {"limit": limit, "offset": offset, **kwargs}
        if category:
            if not isinstance(category, str) or not category.strip():
                raise ValidationError("Category must be a non-empty string")
            params["category"] = category.strip()
            
        return self.client.get("/templates", params=params)
    
    def get_template(self, template_id):
        """Получение информации о шаблоне
        
        Args:
            template_id: ID шаблона
            
        Returns:
            dict: Информация о шаблоне
        """
        self._validate_id(template_id, "template_id")
        return self.client.get(f"/template/{template_id}")