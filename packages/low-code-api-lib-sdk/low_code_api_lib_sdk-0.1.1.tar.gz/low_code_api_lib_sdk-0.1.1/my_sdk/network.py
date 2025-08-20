"""Модуль для сетевого шаринга и работы с сетевыми запросами."""

import json
import time
import socket
import threading
from typing import Dict, Any, Optional, Callable
from urllib.parse import urljoin
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .exceptions import (
    NetworkError, TimeoutError, handle_http_error,
    ConfigurationError, ValidationError
)


class NetworkManager:
    """Менеджер сетевых соединений с поддержкой retry и connection pooling."""
    
    def __init__(self, base_url: str, timeout: int = 30, max_retries: int = 3):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = self._create_session()
        
    def _create_session(self) -> requests.Session:
        """Создание сессии с настройками retry."""
        session = requests.Session()
        
        # Настройка retry стратегии
        retry_strategy = Retry(
            total=self.max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Выполнение HTTP запроса с обработкой ошибок.
        
        Args:
            method: HTTP метод
            endpoint: Конечная точка API
            **kwargs: Дополнительные параметры для requests
            
        Returns:
            Объект ответа requests
            
        Raises:
            NetworkError: При сетевых ошибках
            TimeoutError: При превышении таймаута
        """
        url = urljoin(self.base_url + '/', endpoint.lstrip('/'))
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            )
            
            # Проверка на HTTP ошибки
            if not response.ok:
                handle_http_error(response)
                
            return response
            
        except requests.exceptions.Timeout:
            raise TimeoutError(f"Превышен таймаут запроса к {url}")
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Ошибка соединения с {url}: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Ошибка запроса к {url}: {str(e)}")
    
    def get(self, endpoint: str, **kwargs) -> requests.Response:
        """GET запрос."""
        return self.request('GET', endpoint, **kwargs)
    
    def post(self, endpoint: str, **kwargs) -> requests.Response:
        """POST запрос."""
        return self.request('POST', endpoint, **kwargs)
    
    def put(self, endpoint: str, **kwargs) -> requests.Response:
        """PUT запрос."""
        return self.request('PUT', endpoint, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """DELETE запрос."""
        return self.request('DELETE', endpoint, **kwargs)
    
    def close(self):
        """Закрытие сессии."""
        self.session.close()


class NetworkSharing:
    """Класс для шаринга данных по сети."""
    
    def __init__(self, host: str = 'localhost', port: int = 8080):
        self.host = host
        self.port = port
        self.server_socket = None
        self.is_running = False
        self.clients = []
        self.message_handlers = {}
        
    def start_server(self, callback: Optional[Callable] = None):
        """Запуск сервера для шаринга.
        
        Args:
            callback: Функция обратного вызова для обработки сообщений
        """
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.is_running = True
            
            print(f"Сервер запущен на {self.host}:{self.port}")
            
            while self.is_running:
                try:
                    client_socket, address = self.server_socket.accept()
                    print(f"Подключен клиент: {address}")
                    
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, address, callback)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.error:
                    if self.is_running:
                        raise NetworkError("Ошибка при принятии соединения")
                    
        except socket.error as e:
            raise NetworkError(f"Ошибка запуска сервера: {str(e)}")
    
    def _handle_client(self, client_socket: socket.socket, address: tuple, callback: Optional[Callable]):
        """Обработка клиентского соединения."""
        self.clients.append(client_socket)
        
        try:
            while self.is_running:
                data = client_socket.recv(1024)
                if not data:
                    break
                    
                try:
                    message = json.loads(data.decode('utf-8'))
                    if callback:
                        response = callback(message, address)
                        if response:
                            self.send_to_client(client_socket, response)
                            
                except json.JSONDecodeError:
                    print(f"Получено некорректное JSON сообщение от {address}")
                    
        except socket.error as e:
            print(f"Ошибка при обработке клиента {address}: {str(e)}")
        finally:
            self.clients.remove(client_socket)
            client_socket.close()
            print(f"Клиент {address} отключен")
    
    def send_to_client(self, client_socket: socket.socket, message: Dict[str, Any]):
        """Отправка сообщения клиенту."""
        try:
            data = json.dumps(message).encode('utf-8')
            client_socket.send(data)
        except socket.error as e:
            print(f"Ошибка отправки сообщения клиенту: {str(e)}")
    
    def broadcast_message(self, message: Dict[str, Any]):
        """Отправка сообщения всем подключенным клиентам."""
        disconnected_clients = []
        
        for client in self.clients:
            try:
                self.send_to_client(client, message)
            except:
                disconnected_clients.append(client)
        
        # Удаление отключенных клиентов
        for client in disconnected_clients:
            if client in self.clients:
                self.clients.remove(client)
    
    def stop_server(self):
        """Остановка сервера."""
        self.is_running = False
        
        # Закрытие всех клиентских соединений
        for client in self.clients:
            try:
                client.close()
            except:
                pass
        
        # Закрытие серверного сокета
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        print("Сервер остановлен")
    
    def connect_to_server(self, server_host: str, server_port: int) -> socket.socket:
        """Подключение к серверу шаринга.
        
        Args:
            server_host: Хост сервера
            server_port: Порт сервера
            
        Returns:
            Сокет соединения
            
        Raises:
            NetworkError: При ошибке подключения
        """
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((server_host, server_port))
            return client_socket
        except socket.error as e:
            raise NetworkError(f"Ошибка подключения к серверу {server_host}:{server_port}: {str(e)}")
    
    def send_message(self, client_socket: socket.socket, message: Dict[str, Any]):
        """Отправка сообщения на сервер.
        
        Args:
            client_socket: Сокет клиента
            message: Сообщение для отправки
            
        Raises:
            NetworkError: При ошибке отправки
        """
        try:
            data = json.dumps(message).encode('utf-8')
            client_socket.send(data)
        except socket.error as e:
            raise NetworkError(f"Ошибка отправки сообщения: {str(e)}")


class ConnectionPool:
    """Пул соединений для оптимизации сетевых запросов."""
    
    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self.connections = {}
        self.lock = threading.Lock()
    
    def get_connection(self, base_url: str) -> NetworkManager:
        """Получение соединения из пула.
        
        Args:
            base_url: Базовый URL для соединения
            
        Returns:
            Объект NetworkManager
        """
        with self.lock:
            if base_url not in self.connections:
                if len(self.connections) >= self.max_connections:
                    # Удаление самого старого соединения
                    oldest_key = next(iter(self.connections))
                    self.connections[oldest_key].close()
                    del self.connections[oldest_key]
                
                self.connections[base_url] = NetworkManager(base_url)
            
            return self.connections[base_url]
    
    def close_all(self):
        """Закрытие всех соединений в пуле."""
        with self.lock:
            for connection in self.connections.values():
                connection.close()
            self.connections.clear()


# Глобальный пул соединений
_connection_pool = ConnectionPool()


def get_network_manager(base_url: str) -> NetworkManager:
    """Получение менеджера сети из глобального пула.
    
    Args:
        base_url: Базовый URL
        
    Returns:
        Объект NetworkManager
    """
    return _connection_pool.get_connection(base_url)


def close_all_connections():
    """Закрытие всех соединений в глобальном пуле."""
    _connection_pool.close_all()