"""Тесты для модуля исключений SDK."""

import unittest
from unittest.mock import Mock
import sys
import os

# Добавляем путь к модулю SDK
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from my_sdk.exceptions import (
    SDKError, AuthenticationError, AuthorizationError, ValidationError,
    NetworkError, TimeoutError, ServerError, ClientError, NotFoundError,
    RateLimitError, ConfigurationError, APIError, handle_http_error,
    validate_token, validate_base_url
)


class TestSDKExceptions(unittest.TestCase):
    """Тесты для исключений SDK."""
    
    def test_sdk_error_base_class(self):
        """Тест базового класса SDKError."""
        message = "Test error"
        status_code = 500
        response = Mock()
        
        error = SDKError(message, status_code, response)
        
        self.assertEqual(str(error), message)
        self.assertEqual(error.message, message)
        self.assertEqual(error.status_code, status_code)
        self.assertEqual(error.response, response)
    
    def test_authentication_error(self):
        """Тест ошибки аутентификации."""
        error = AuthenticationError("Invalid token")
        self.assertIsInstance(error, SDKError)
        self.assertEqual(str(error), "Invalid token")
    
    def test_authorization_error(self):
        """Тест ошибки авторизации."""
        error = AuthorizationError("Access denied")
        self.assertIsInstance(error, SDKError)
        self.assertEqual(str(error), "Access denied")
    
    def test_validation_error(self):
        """Тест ошибки валидации."""
        error = ValidationError("Invalid data")
        self.assertIsInstance(error, SDKError)
        self.assertEqual(str(error), "Invalid data")
    
    def test_network_error(self):
        """Тест сетевой ошибки."""
        error = NetworkError("Connection failed")
        self.assertIsInstance(error, SDKError)
        self.assertEqual(str(error), "Connection failed")
    
    def test_timeout_error(self):
        """Тест ошибки таймаута."""
        error = TimeoutError("Request timeout")
        self.assertIsInstance(error, SDKError)
        self.assertEqual(str(error), "Request timeout")
    
    def test_server_error(self):
        """Тест серверной ошибки."""
        error = ServerError("Internal server error")
        self.assertIsInstance(error, SDKError)
        self.assertEqual(str(error), "Internal server error")
    
    def test_client_error(self):
        """Тест клиентской ошибки."""
        error = ClientError("Bad request")
        self.assertIsInstance(error, SDKError)
        self.assertEqual(str(error), "Bad request")
    
    def test_not_found_error(self):
        """Тест ошибки 'не найдено'."""
        error = NotFoundError("Resource not found")
        self.assertIsInstance(error, ClientError)
        self.assertEqual(str(error), "Resource not found")
    
    def test_rate_limit_error(self):
        """Тест ошибки превышения лимита запросов."""
        error = RateLimitError("Rate limit exceeded")
        self.assertIsInstance(error, ClientError)
        self.assertEqual(str(error), "Rate limit exceeded")


class TestHTTPErrorHandler(unittest.TestCase):
    """Тесты для обработчика HTTP ошибок."""
    
    def create_mock_response(self, status_code, json_data=None, text=""):
        """Создание мока ответа."""
        response = Mock()
        response.status_code = status_code
        response.text = text
        
        if json_data:
            response.json.return_value = json_data
        else:
            response.json.side_effect = ValueError("No JSON")
        
        return response
    
    def test_handle_401_error(self):
        """Тест обработки ошибки 401."""
        response = self.create_mock_response(401, {"message": "Unauthorized"})
        
        with self.assertRaises(AuthenticationError) as context:
            handle_http_error(response)
        
        self.assertEqual(str(context.exception), "Unauthorized")
        self.assertEqual(context.exception.status_code, 401)
    
    def test_handle_403_error(self):
        """Тест обработки ошибки 403."""
        response = self.create_mock_response(403, {"message": "Forbidden"})
        
        with self.assertRaises(AuthorizationError) as context:
            handle_http_error(response)
        
        self.assertEqual(str(context.exception), "Forbidden")
    
    def test_handle_404_error(self):
        """Тест обработки ошибки 404."""
        response = self.create_mock_response(404, {"message": "Not found"})
        
        with self.assertRaises(NotFoundError) as context:
            handle_http_error(response)
        
        self.assertEqual(str(context.exception), "Not found")
    
    def test_handle_429_error(self):
        """Тест обработки ошибки 429."""
        response = self.create_mock_response(429, {"message": "Rate limit exceeded"})
        
        with self.assertRaises(RateLimitError) as context:
            handle_http_error(response)
        
        self.assertEqual(str(context.exception), "Rate limit exceeded")
    
    def test_handle_400_error(self):
        """Тест обработки ошибки 400."""
        response = self.create_mock_response(400, {"message": "Bad request"})
        
        with self.assertRaises(ClientError) as context:
            handle_http_error(response)
        
        self.assertEqual(str(context.exception), "Bad request")
    
    def test_handle_500_error(self):
        """Тест обработки ошибки 500."""
        response = self.create_mock_response(500, {"message": "Internal server error"})
        
        with self.assertRaises(ServerError) as context:
            handle_http_error(response)
        
        self.assertEqual(str(context.exception), "Internal server error")
    
    def test_handle_error_without_json(self):
        """Тест обработки ошибки без JSON."""
        response = self.create_mock_response(500, text="Internal Server Error")
        
        with self.assertRaises(ServerError) as context:
            handle_http_error(response)
        
        self.assertIn("HTTP 500 Error", str(context.exception))
    
    def test_handle_unknown_error(self):
        """Тест обработки неизвестной ошибки."""
        response = self.create_mock_response(999, {"message": "Unknown error"})
        
        with self.assertRaises(APIError) as context:
            handle_http_error(response)
        
        self.assertEqual(str(context.exception), "Unknown error")


class TestValidationFunctions(unittest.TestCase):
    """Тесты для функций валидации."""
    
    def test_validate_token_valid(self):
        """Тест валидации корректного токена."""
        # Не должно выбрасывать исключение
        validate_token("valid_token")
    
    def test_validate_token_empty(self):
        """Тест валидации пустого токена."""
        with self.assertRaises(ValidationError) as context:
            validate_token("")
        
        self.assertIn("не может быть пустым", str(context.exception))
    
    def test_validate_token_none(self):
        """Тест валидации None токена."""
        with self.assertRaises(ValidationError) as context:
            validate_token(None)
        
        self.assertIn("не может быть пустым", str(context.exception))
    
    def test_validate_token_not_string(self):
        """Тест валидации токена не строкового типа."""
        with self.assertRaises(ValidationError) as context:
            validate_token(123)
        
        self.assertIn("должен быть строкой", str(context.exception))
    
    def test_validate_token_whitespace_only(self):
        """Тест валидации токена из пробелов."""
        with self.assertRaises(ValidationError) as context:
            validate_token("   ")
        
        self.assertIn("не может состоять только из пробелов", str(context.exception))
    
    def test_validate_base_url_valid_http(self):
        """Тест валидации корректного HTTP URL."""
        validate_base_url("http://example.com")
    
    def test_validate_base_url_valid_https(self):
        """Тест валидации корректного HTTPS URL."""
        validate_base_url("https://example.com")
    
    def test_validate_base_url_empty(self):
        """Тест валидации пустого URL."""
        with self.assertRaises(ValidationError) as context:
            validate_base_url("")
        
        self.assertIn("не может быть пустым", str(context.exception))
    
    def test_validate_base_url_not_string(self):
        """Тест валидации URL не строкового типа."""
        with self.assertRaises(ValidationError) as context:
            validate_base_url(123)
        
        self.assertIn("должен быть строкой", str(context.exception))
    
    def test_validate_base_url_invalid_protocol(self):
        """Тест валидации URL с неверным протоколом."""
        with self.assertRaises(ValidationError) as context:
            validate_base_url("ftp://example.com")
        
        self.assertIn("должен начинаться с http://", str(context.exception))


if __name__ == '__main__':
    unittest.main()