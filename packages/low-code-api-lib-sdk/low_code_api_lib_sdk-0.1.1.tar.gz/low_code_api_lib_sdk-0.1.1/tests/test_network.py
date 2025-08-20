"""Тесты для сетевого модуля SDK."""

import unittest
from unittest.mock import Mock, patch, MagicMock
import socket
import json
import sys
import os

# Добавляем путь к модулю SDK
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from my_sdk.network import (
    NetworkManager, NetworkSharing, ConnectionPool,
    get_network_manager, close_all_connections
)
from my_sdk.exceptions import NetworkError, TimeoutError


class TestNetworkManager(unittest.TestCase):
    """Тесты для класса NetworkManager."""
    
    def setUp(self):
        """Настройка тестов."""
        self.base_url = "https://api.example.com"
        self.manager = NetworkManager(self.base_url)
    
    def test_init(self):
        """Тест инициализации NetworkManager."""
        self.assertEqual(self.manager.base_url, self.base_url)
        self.assertEqual(self.manager.timeout, 30)
        self.assertEqual(self.manager.max_retries, 3)
        self.assertIsNotNone(self.manager.session)
    
    def test_init_with_custom_params(self):
        """Тест инициализации с кастомными параметрами."""
        manager = NetworkManager(self.base_url, timeout=60, max_retries=5)
        self.assertEqual(manager.timeout, 60)
        self.assertEqual(manager.max_retries, 5)
    
    def test_base_url_normalization(self):
        """Тест нормализации базового URL."""
        manager = NetworkManager("https://api.example.com/")
        self.assertEqual(manager.base_url, "https://api.example.com")
    
    @patch('requests.Session.request')
    def test_successful_request(self, mock_request):
        """Тест успешного запроса."""
        # Настройка мока
        mock_response = Mock()
        mock_response.ok = True
        mock_request.return_value = mock_response
        
        # Выполнение запроса
        response = self.manager.request('GET', '/test')
        
        # Проверки
        self.assertEqual(response, mock_response)
        mock_request.assert_called_once()
        
        # Проверка URL
        call_args = mock_request.call_args
        self.assertEqual(call_args[1]['url'], 'https://api.example.com/test')
    
    @patch('requests.Session.request')
    def test_request_with_timeout_error(self, mock_request):
        """Тест запроса с ошибкой таймаута."""
        import requests
        mock_request.side_effect = requests.exceptions.Timeout()
        
        with self.assertRaises(TimeoutError):
            self.manager.request('GET', '/test')
    
    @patch('requests.Session.request')
    def test_request_with_connection_error(self, mock_request):
        """Тест запроса с ошибкой соединения."""
        import requests
        mock_request.side_effect = requests.exceptions.ConnectionError()
        
        with self.assertRaises(NetworkError):
            self.manager.request('GET', '/test')
    
    @patch('requests.Session.request')
    def test_get_request(self, mock_request):
        """Тест GET запроса."""
        mock_response = Mock()
        mock_response.ok = True
        mock_request.return_value = mock_response
        
        self.manager.get('/test')
        
        call_args = mock_request.call_args
        self.assertEqual(call_args[1]['method'], 'GET')
    
    @patch('requests.Session.request')
    def test_post_request(self, mock_request):
        """Тест POST запроса."""
        mock_response = Mock()
        mock_response.ok = True
        mock_request.return_value = mock_response
        
        self.manager.post('/test', json={'data': 'test'})
        
        call_args = mock_request.call_args
        self.assertEqual(call_args[1]['method'], 'POST')
        self.assertEqual(call_args[1]['json'], {'data': 'test'})
    
    def test_close_session(self):
        """Тест закрытия сессии."""
        with patch.object(self.manager.session, 'close') as mock_close:
            self.manager.close()
            mock_close.assert_called_once()


class TestNetworkSharing(unittest.TestCase):
    """Тесты для класса NetworkSharing."""
    
    def setUp(self):
        """Настройка тестов."""
        self.sharing = NetworkSharing('localhost', 8080)
    
    def test_init(self):
        """Тест инициализации NetworkSharing."""
        self.assertEqual(self.sharing.host, 'localhost')
        self.assertEqual(self.sharing.port, 8080)
        self.assertFalse(self.sharing.is_running)
        self.assertEqual(self.sharing.clients, [])
    
    def test_init_with_defaults(self):
        """Тест инициализации с параметрами по умолчанию."""
        sharing = NetworkSharing()
        self.assertEqual(sharing.host, 'localhost')
        self.assertEqual(sharing.port, 8080)
    
    @patch('socket.socket')
    def test_start_server_socket_creation(self, mock_socket_class):
        """Тест создания сокета при запуске сервера."""
        mock_socket = Mock()
        mock_socket_class.return_value = mock_socket
        mock_socket.accept.side_effect = socket.error("Test stop")
        
        try:
            self.sharing.start_server()
        except NetworkError:
            pass  # Ожидаемая ошибка
        
        # Проверки
        mock_socket_class.assert_called_with(socket.AF_INET, socket.SOCK_STREAM)
        mock_socket.setsockopt.assert_called_with(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        mock_socket.bind.assert_called_with(('localhost', 8080))
        mock_socket.listen.assert_called_with(5)
    
    @patch('socket.socket')
    def test_connect_to_server(self, mock_socket_class):
        """Тест подключения к серверу."""
        mock_socket = Mock()
        mock_socket_class.return_value = mock_socket
        
        result = self.sharing.connect_to_server('localhost', 9000)
        
        self.assertEqual(result, mock_socket)
        mock_socket.connect.assert_called_with(('localhost', 9000))
    
    @patch('socket.socket')
    def test_connect_to_server_error(self, mock_socket_class):
        """Тест ошибки подключения к серверу."""
        mock_socket = Mock()
        mock_socket_class.return_value = mock_socket
        mock_socket.connect.side_effect = socket.error("Connection failed")
        
        with self.assertRaises(NetworkError):
            self.sharing.connect_to_server('localhost', 9000)
    
    def test_send_message_to_client(self):
        """Тест отправки сообщения клиенту."""
        mock_socket = Mock()
        message = {'type': 'test', 'data': 'hello'}
        
        self.sharing.send_to_client(mock_socket, message)
        
        expected_data = json.dumps(message).encode('utf-8')
        mock_socket.send.assert_called_with(expected_data)
    
    def test_send_message_to_client_error(self):
        """Тест ошибки отправки сообщения клиенту."""
        mock_socket = Mock()
        mock_socket.send.side_effect = socket.error("Send failed")
        message = {'type': 'test'}
        
        # Не должно выбрасывать исключение, только печатать ошибку
        with patch('builtins.print') as mock_print:
            self.sharing.send_to_client(mock_socket, message)
            mock_print.assert_called()
    
    def test_broadcast_message(self):
        """Тест широковещательной отправки сообщения."""
        mock_client1 = Mock()
        mock_client2 = Mock()
        self.sharing.clients = [mock_client1, mock_client2]
        
        message = {'type': 'broadcast', 'data': 'hello all'}
        
        with patch.object(self.sharing, 'send_to_client') as mock_send:
            self.sharing.broadcast_message(message)
            
            self.assertEqual(mock_send.call_count, 2)
            mock_send.assert_any_call(mock_client1, message)
            mock_send.assert_any_call(mock_client2, message)
    
    def test_broadcast_message_with_disconnected_clients(self):
        """Тест широковещательной отправки с отключенными клиентами."""
        mock_client1 = Mock()
        mock_client2 = Mock()
        self.sharing.clients = [mock_client1, mock_client2]
        
        message = {'type': 'broadcast'}
        
        with patch.object(self.sharing, 'send_to_client') as mock_send:
            # Первый клиент работает, второй отключен
            mock_send.side_effect = [None, Exception("Disconnected")]
            
            self.sharing.broadcast_message(message)
            
            # Отключенный клиент должен быть удален
            self.assertEqual(len(self.sharing.clients), 1)
            self.assertIn(mock_client1, self.sharing.clients)
            self.assertNotIn(mock_client2, self.sharing.clients)
    
    def test_stop_server(self):
        """Тест остановки сервера."""
        mock_client1 = Mock()
        mock_client2 = Mock()
        mock_server_socket = Mock()
        
        self.sharing.clients = [mock_client1, mock_client2]
        self.sharing.server_socket = mock_server_socket
        self.sharing.is_running = True
        
        with patch('builtins.print') as mock_print:
            self.sharing.stop_server()
            
            # Проверки
            self.assertFalse(self.sharing.is_running)
            mock_client1.close.assert_called_once()
            mock_client2.close.assert_called_once()
            mock_server_socket.close.assert_called_once()
            mock_print.assert_called_with("Сервер остановлен")
    
    def test_send_message_to_server(self):
        """Тест отправки сообщения на сервер."""
        mock_socket = Mock()
        message = {'type': 'client_message', 'data': 'hello server'}
        
        self.sharing.send_message(mock_socket, message)
        
        expected_data = json.dumps(message).encode('utf-8')
        mock_socket.send.assert_called_with(expected_data)
    
    def test_send_message_to_server_error(self):
        """Тест ошибки отправки сообщения на сервер."""
        mock_socket = Mock()
        mock_socket.send.side_effect = socket.error("Send failed")
        message = {'type': 'test'}
        
        with self.assertRaises(NetworkError):
            self.sharing.send_message(mock_socket, message)


class TestConnectionPool(unittest.TestCase):
    """Тесты для класса ConnectionPool."""
    
    def setUp(self):
        """Настройка тестов."""
        self.pool = ConnectionPool(max_connections=2)
    
    def test_init(self):
        """Тест инициализации пула соединений."""
        self.assertEqual(self.pool.max_connections, 2)
        self.assertEqual(self.pool.connections, {})
    
    @patch('my_sdk.network.NetworkManager')
    def test_get_connection_new(self, mock_network_manager):
        """Тест получения нового соединения."""
        base_url = "https://api.example.com"
        mock_manager = Mock()
        mock_network_manager.return_value = mock_manager
        
        result = self.pool.get_connection(base_url)
        
        self.assertEqual(result, mock_manager)
        mock_network_manager.assert_called_with(base_url)
        self.assertIn(base_url, self.pool.connections)
    
    @patch('my_sdk.network.NetworkManager')
    def test_get_connection_existing(self, mock_network_manager):
        """Тест получения существующего соединения."""
        base_url = "https://api.example.com"
        mock_manager = Mock()
        self.pool.connections[base_url] = mock_manager
        
        result = self.pool.get_connection(base_url)
        
        self.assertEqual(result, mock_manager)
        # NetworkManager не должен создаваться заново
        mock_network_manager.assert_not_called()
    
    @patch('my_sdk.network.NetworkManager')
    def test_get_connection_max_limit(self, mock_network_manager):
        """Тест превышения лимита соединений."""
        # Заполняем пул до максимума
        mock_manager1 = Mock()
        mock_manager2 = Mock()
        self.pool.connections["url1"] = mock_manager1
        self.pool.connections["url2"] = mock_manager2
        
        # Добавляем новое соединение
        new_url = "https://new.example.com"
        mock_new_manager = Mock()
        mock_network_manager.return_value = mock_new_manager
        
        result = self.pool.get_connection(new_url)
        
        # Проверяем, что старое соединение закрыто и удалено
        mock_manager1.close.assert_called_once()
        self.assertNotIn("url1", self.pool.connections)
        self.assertIn(new_url, self.pool.connections)
        self.assertEqual(result, mock_new_manager)
    
    def test_close_all_connections(self):
        """Тест закрытия всех соединений."""
        mock_manager1 = Mock()
        mock_manager2 = Mock()
        self.pool.connections["url1"] = mock_manager1
        self.pool.connections["url2"] = mock_manager2
        
        self.pool.close_all()
        
        mock_manager1.close.assert_called_once()
        mock_manager2.close.assert_called_once()
        self.assertEqual(self.pool.connections, {})


class TestGlobalFunctions(unittest.TestCase):
    """Тесты для глобальных функций модуля."""
    
    @patch('my_sdk.network._connection_pool')
    def test_get_network_manager(self, mock_pool):
        """Тест получения менеджера сети."""
        base_url = "https://api.example.com"
        mock_manager = Mock()
        mock_pool.get_connection.return_value = mock_manager
        
        result = get_network_manager(base_url)
        
        self.assertEqual(result, mock_manager)
        mock_pool.get_connection.assert_called_with(base_url)
    
    @patch('my_sdk.network._connection_pool')
    def test_close_all_connections_global(self, mock_pool):
        """Тест закрытия всех соединений через глобальную функцию."""
        close_all_connections()
        mock_pool.close_all.assert_called_once()


if __name__ == '__main__':
    unittest.main()