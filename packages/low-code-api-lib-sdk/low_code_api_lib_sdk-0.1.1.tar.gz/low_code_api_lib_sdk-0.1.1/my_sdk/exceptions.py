"""Модуль обработки ошибок для Low Code API Lib SDK."""


class SDKError(Exception):
    """Базовый класс для всех ошибок SDK."""
    
    def __init__(self, message, status_code=None, response=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response = response


class AuthenticationError(SDKError):
    """Ошибка аутентификации."""
    pass


class AuthorizationError(SDKError):
    """Ошибка авторизации (недостаточно прав)."""
    pass


class ValidationError(SDKError):
    """Ошибка валидации данных."""
    pass


class NetworkError(SDKError):
    """Ошибка сети."""
    pass


class TimeoutError(SDKError):
    """Ошибка таймаута."""
    pass


class ServerError(SDKError):
    """Ошибка сервера (5xx)."""
    pass


class ClientError(SDKError):
    """Ошибка клиента (4xx)."""
    pass


class NotFoundError(ClientError):
    """Ресурс не найден (404)."""
    pass


class RateLimitError(ClientError):
    """Превышен лимит запросов."""
    pass


class ConfigurationError(SDKError):
    """Ошибка конфигурации SDK."""
    pass


class APIError(SDKError):
    """Общая ошибка API."""
    pass


def handle_http_error(response):
    """Обработчик HTTP ошибок.
    
    Args:
        response: Объект ответа requests
        
    Raises:
        Соответствующее исключение в зависимости от статус кода
    """
    status_code = response.status_code
    
    try:
        error_data = response.json()
        message = error_data.get('message', f'HTTP {status_code} Error')
    except ValueError:
        message = f'HTTP {status_code} Error: {response.text}'
    
    if status_code == 401:
        raise AuthenticationError(message, status_code, response)
    elif status_code == 403:
        raise AuthorizationError(message, status_code, response)
    elif status_code == 404:
        raise NotFoundError(message, status_code, response)
    elif status_code == 429:
        raise RateLimitError(message, status_code, response)
    elif 400 <= status_code < 500:
        raise ClientError(message, status_code, response)
    elif 500 <= status_code < 600:
        raise ServerError(message, status_code, response)
    else:
        raise APIError(message, status_code, response)


def validate_token(token):
    """Валидация токена авторизации.
    
    Args:
        token: Токен для валидации
        
    Raises:
        ValidationError: Если токен невалиден
    """
    if not token:
        raise ValidationError("Токен авторизации не может быть пустым")
    
    if not isinstance(token, str):
        raise ValidationError("Токен авторизации должен быть строкой")
    
    if len(token.strip()) == 0:
        raise ValidationError("Токен авторизации не может состоять только из пробелов")


def validate_base_url(base_url):
    """Валидация базового URL.
    
    Args:
        base_url: URL для валидации
        
    Raises:
        ValidationError: Если URL невалиден
    """
    if not base_url:
        raise ValidationError("Базовый URL не может быть пустым")
    
    if not isinstance(base_url, str):
        raise ValidationError("Базовый URL должен быть строкой")
    
    if not (base_url.startswith('http://') or base_url.startswith('https://')):
        raise ValidationError("Базовый URL должен начинаться с http:// или https://")