from .base import BaseModule

class Auth(BaseModule):
    """Модуль для работы с аутентификацией"""
    
    def login(self, username, password):
        """Вход в систему
        
        Args:
            username: Имя пользователя
            password: Пароль пользователя
            
        Returns:
            dict: Результат запроса
        """
        data = {
            "username": username,
            "password": password
        }
        return self.client.post("/login", data)
    
    def register(self, username, password, email, **kwargs):
        """Регистрация нового пользователя
        
        Args:
            username: Имя пользователя
            password: Пароль пользователя
            email: Email пользователя
            **kwargs: Дополнительные параметры
            
        Returns:
            dict: Результат запроса
        """
        data = {
            "username": username,
            "password": password,
            "email": email,
            **kwargs
        }
        return self.client.post("/register", data)
    
    def logout(self):
        """Выход из системы
        
        Returns:
            dict: Результат запроса
        """
        return self.client.get("/logout")