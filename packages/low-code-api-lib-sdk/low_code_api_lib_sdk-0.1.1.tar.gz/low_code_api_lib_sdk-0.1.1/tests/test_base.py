"""Тесты для базовой функциональности SDK."""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# Добавляем путь к модулю SDK
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from my_sdk.base import BaseModule
from my_sdk.client import Client
from my_sdk.exceptions import ValidationError, AuthenticationError


class TestBaseModule(unittest.TestCase):
    """Тесты для класса BaseModule."""
    
    def setUp(self):
        """Настройка тестов."""
        self.base_url = "https://api.example.com"
        self.token = "test_token_123"
        self.client = Client(token=self.token, base_url=self.base_url)
        self.base_module = BaseModule(self.client)
    
    def test_init_with_valid_params(self):
        """Тест инициализации с валидными параметрами."""
        client = Client(token="valid_token", base_url="https://valid.url")
        module = BaseModule(client)
        self.assertEqual(module.client, client)
        self.assertIsNotNone(module.client)
    
    def test_init_without_token(self):
        """Тест инициализации без токена."""
        with self.assertRaises(TypeError):
            Client(base_url="https://valid.url")
    
    def test_init_without_base_url(self):
        """Тест инициализации без базового URL."""
        # Client должен работать с токеном и базовым URL по умолчанию
        client = Client(token="valid_token")
        self.assertEqual(client.base_url, "https://soundrush.live/api_dev")
    
    def test_init_with_invalid_url(self):
        """Тест инициализации с невалидным URL."""
        with self.assertRaises(ValidationError):
            Client(token="valid_token", base_url="invalid_url")
    
    def test_validate_id_valid(self):
        """Тест валидации корректного ID."""
        # Не должно вызывать исключение
        self.base_module._validate_id("123", "test_id")
        self.base_module._validate_id(123, "test_id")
    
    def test_validate_id_invalid(self):
        """Тест валидации некорректного ID."""
        with self.assertRaises(ValidationError):
            self.base_module._validate_id("", "test_id")
        with self.assertRaises(ValidationError):
            self.base_module._validate_id(None, "test_id")
        with self.assertRaises(ValidationError):
            self.base_module._validate_id(0, "test_id")
    
    def test_validate_required_params_valid(self):
        """Тест валидации корректных обязательных параметров."""
        params = {"name": "test", "email": "test@example.com"}
        required = ["name", "email"]
        # Не должно вызывать исключение
        self.base_module._validate_required_params(params, required)
    
    def test_validate_required_params_missing(self):
        """Тест валидации с отсутствующими обязательными параметрами."""
        params = {"name": "test"}
        required = ["name", "email"]
        with self.assertRaises(ValidationError):
            self.base_module._validate_required_params(params, required)


if __name__ == '__main__':
    unittest.main()