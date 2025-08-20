import requests
from .exceptions import (
    SDKError, AuthenticationError, ValidationError, 
    ConfigurationError, handle_http_error, validate_token, validate_base_url
)
from .network import get_network_manager

class Client:
    def __init__(self, token, base_url="https://soundrush.live/api_dev"):
        # Валидация входных параметров
        validate_token(token)
        validate_base_url(base_url)
        
        self.token = token
        self.base_url = base_url.rstrip('/')
        
        # Инициализация сетевого менеджера
        self.network_manager = get_network_manager(self.base_url)
        
        # Заголовки по умолчанию
        self.default_headers = {
            "Authorization": self.token,
            "Content-Type": "application/json",
            "User-Agent": "Low-Code-API-Lib-SDK/0.1.1"
        }
        
    def _handle_json_response(self, response, method_name=""):
        """Helper method to handle JSON responses and errors consistently"""
        # Проверка на HTTP ошибки
        if not response.ok:
            handle_http_error(response)
        
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            # Если JSON не удалось декодировать, но статус успешный
            if response.status_code == 204:  # No Content
                return {"success": True}
            
            raise SDKError(
                f"Could not decode JSON response from {method_name}. Status code: {response.status_code}",
                status_code=response.status_code,
                response=response
            )


    def get(self, endpoint, **kwargs):
        """Выполнение GET запроса с обработкой ошибок."""
        headers = {**self.default_headers, **kwargs.pop('headers', {})}
        response = self.network_manager.get(endpoint, headers=headers, **kwargs)
        return self._handle_json_response(response, "GET")
        
    def post(self, endpoint, data=None, **kwargs):
        """Выполнение POST запроса с обработкой ошибок."""
        headers = {**self.default_headers, **kwargs.pop('headers', {})}
        response = self.network_manager.post(endpoint, json=data, headers=headers, **kwargs)
        return self._handle_json_response(response, "POST")
        
    def put(self, endpoint, data=None, **kwargs):
        """Выполнение PUT запроса с обработкой ошибок."""
        headers = {**self.default_headers, **kwargs.pop('headers', {})}
        response = self.network_manager.put(endpoint, json=data, headers=headers, **kwargs)
        return self._handle_json_response(response, "PUT")
        
    def delete(self, endpoint, **kwargs):
        """Выполнение DELETE запроса с обработкой ошибок."""
        headers = {**self.default_headers, **kwargs.pop('headers', {})}
        response = self.network_manager.delete(endpoint, headers=headers, **kwargs)
        return self._handle_json_response(response, "DELETE")
        
    def patch(self, endpoint, data=None, **kwargs):
        """Выполнение PATCH запроса с обработкой ошибок."""
        headers = {**self.default_headers, **kwargs.pop('headers', {})}
        response = self.network_manager.request('PATCH', endpoint, json=data, headers=headers, **kwargs)
        return self._handle_json_response(response, "PATCH")


    # Методы для создания экземпляров модулей API
    def auth(self):
        from .auth import Auth
        return Auth(self)
        
    def user(self):
        from .user import User
        return User(self)
        
    def bots(self):
        from .bots import Bots
        return Bots(self)
        
    def templates(self):
        from .templates import Templates
        return Templates(self)
        
    def media(self):
        from .media import Media
        return Media(self)
        
    def visual_editor(self):
        from .visual_editor import VisualEditor
        return VisualEditor(self)
        
    def admin(self):
        from .admin import Admin
        return Admin(self)
        
    def system(self):
        from .system import System
        return System(self)
    
    def __str__(self):
        """Строковое представление клиента."""
        return f"Client(base_url='{self.base_url}')"


if __name__ == "__main__":
    client = Client("123")
    # Get user data
    get_result = client.get("/api/user/info")
    print("GET result:", get_result)
    
    # Post user data using user module
    user = client.user()
    user_info = user.get_info()
    print("User info:", user_info)
