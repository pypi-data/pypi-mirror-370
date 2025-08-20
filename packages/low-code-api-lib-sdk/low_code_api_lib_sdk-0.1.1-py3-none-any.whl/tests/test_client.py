"""Тесты для клиента SDK."""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# Добавляем путь к модулю SDK
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from my_sdk.client import Client
from my_sdk.exceptions import ValidationError
from my_sdk.auth import Auth
from my_sdk.user import User
from my_sdk.bots import Bots


class TestClient(unittest.TestCase):
    """Тесты для класса Client."""
    
    def setUp(self):
        """Настройка тестов."""
        self.token = "test_token"
        self.base_url = "https://api.example.com"
        self.client = Client(token=self.token, base_url=self.base_url)
    
    def test_init_with_token_only(self):
        """Тест инициализации только с токеном."""
        client = Client(token=self.token)
        self.assertEqual(client.token, self.token)
        self.assertEqual(client.base_url, "https://soundrush.live/api_dev")
    
    def test_init_with_token_and_base_url(self):
        """Тест инициализации с токеном и базовым URL."""
        self.assertEqual(self.client.token, self.token)
        self.assertEqual(self.client.base_url, self.base_url)
    
    def test_init_without_token(self):
        """Тест инициализации без токена."""
        with self.assertRaises(ValidationError):
            Client(token="")
        with self.assertRaises(TypeError):
            Client()
    
    def test_init_with_invalid_base_url(self):
        """Тест инициализации с невалидным базовым URL."""
        with self.assertRaises(ValidationError):
            Client(token=self.token, base_url="invalid_url")
    
    def test_auth_module_creation(self):
        """Тест создания модуля аутентификации."""
        auth = self.client.auth()
        self.assertIsInstance(auth, Auth)
        self.assertEqual(auth.client, self.client)
    
    def test_user_module_creation(self):
        """Тест создания модуля пользователя."""
        user = self.client.user()
        self.assertIsInstance(user, User)
        self.assertEqual(user.client, self.client)
    
    def test_bots_module_creation(self):
        """Тест создания модуля ботов."""
        bots = self.client.bots()
        self.assertIsInstance(bots, Bots)
        self.assertEqual(bots.client, self.client)
    
    def test_templates_module_creation(self):
        """Тест создания модуля шаблонов."""
        templates = self.client.templates()
        self.assertEqual(templates.client, self.client)
    
    def test_media_module_creation(self):
        """Тест создания модуля медиа."""
        media = self.client.media()
        self.assertEqual(media.client, self.client)
    
    def test_visual_editor_module_creation(self):
        """Тест создания модуля визуального редактора."""
        visual_editor = self.client.visual_editor()
        self.assertEqual(visual_editor.client, self.client)
    
    def test_admin_module_creation(self):
        """Тест создания модуля администратора."""
        admin = self.client.admin()
        self.assertEqual(admin.client, self.client)
    
    def test_system_module_creation(self):
        """Тест создания модуля системы."""
        system = self.client.system()
        self.assertEqual(system.client, self.client)
    
    def test_multiple_module_instances(self):
        """Тест создания нескольких экземпляров модулей."""
        auth1 = self.client.auth()
        auth2 = self.client.auth()
        
        # Должны быть разными объектами
        self.assertIsNot(auth1, auth2)
        
        # Но с одинаковым клиентом
        self.assertEqual(auth1.client, auth2.client)
    
    def test_client_string_representation(self):
        """Тест строкового представления клиента."""
        client_str = str(self.client)
        self.assertIn("Client", client_str)
        self.assertIn(self.base_url, client_str)
        # Токен не должен отображаться в строковом представлении
        self.assertNotIn(self.token, client_str)


if __name__ == '__main__':
    unittest.main()