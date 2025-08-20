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
            
        Raises:
            ValidationError: Если параметры невалидны
            AuthenticationError: Если аутентификация не удалась
        """
        # Валидация входных параметров
        params = {"username": username, "password": password}
        self._validate_required_params(params, ["username", "password"])
        
        if not isinstance(username, str) or len(username.strip()) < 3:
            raise ValidationError("Имя пользователя должно содержать минимум 3 символа")
        
        if not isinstance(password, str) or len(password) < 6:
            raise ValidationError("Пароль должен содержать минимум 6 символов")
        
        data = {
            "username": username.strip(),
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
            
        Raises:
            ValidationError: Если параметры невалидны
        """
        # Валидация входных параметров
        params = {"username": username, "password": password, "email": email}
        self._validate_required_params(params, ["username", "password", "email"])
        
        if not isinstance(username, str) or len(username.strip()) < 3:
            raise ValidationError("Имя пользователя должно содержать минимум 3 символа")
        
        if not isinstance(password, str) or len(password) < 6:
            raise ValidationError("Пароль должен содержать минимум 6 символов")
        
        # Простая валидация email
        if not isinstance(email, str) or "@" not in email or "." not in email:
            raise ValidationError("Некорректный формат email")
        
        data = {
            "username": username.strip(),
            "password": password,
            "email": email.strip().lower(),
            **kwargs
        }
        return self.client.post("/register", data)
    
    def logout(self):
        """Выход из системы
        
        Returns:
            dict: Результат запроса
        """
        return self.client.get("/logout")
    
    def get_me(self):
        """Получение информации о текущем пользователе
        
        Returns:
            dict: Информация о пользователе
            
        Raises:
            AuthenticationError: Если пользователь не аутентифицирован
        """
        return self.client.get("/api/auth/me")