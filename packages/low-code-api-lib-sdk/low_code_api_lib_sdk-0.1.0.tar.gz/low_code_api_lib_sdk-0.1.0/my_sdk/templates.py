from .base import BaseModule

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
        return self.client.post(f"/template/{template_id}/download", kwargs)
    
    def rate(self, template_id, rating, **kwargs):
        """Оценка шаблона
        
        Args:
            template_id: ID шаблона
            rating: Оценка
            **kwargs: Дополнительные параметры
            
        Returns:
            dict: Результат запроса
        """
        data = {"rating": rating, **kwargs}
        return self.client.post(f"/template/{template_id}/rate", data)
    
    def comment(self, template_id, comment_text, **kwargs):
        """Добавление комментария к шаблону
        
        Args:
            template_id: ID шаблона
            comment_text: Текст комментария
            **kwargs: Дополнительные параметры
            
        Returns:
            dict: Результат запроса
        """
        data = {"comment": comment_text, **kwargs}
        return self.client.post(f"/template/{template_id}/comment", data)
    
    def use_template(self, template_id, **kwargs):
        """Использование шаблона для создания бота
        
        Args:
            template_id: ID шаблона
            **kwargs: Дополнительные параметры
            
        Returns:
            dict: Результат запроса
        """
        return self.client.post(f"/use_template/{template_id}", kwargs)
    
    def toggle_favorite(self, template_id, **kwargs):
        """Добавление/удаление шаблона из избранного
        
        Args:
            template_id: ID шаблона
            **kwargs: Дополнительные параметры
            
        Returns:
            dict: Результат запроса
        """
        return self.client.post(f"/templates/favorite/{template_id}", kwargs)