from .client import Client
from .auth import Auth
from .user import User
from .bots import Bots
from .templates import Templates
from .media import Media
from .visual_editor import VisualEditor
from .admin import Admin
from .system import System

# Новые модули в версии 0.1.1
from . import exceptions
from . import network

__all__ = [
    'Client', 'Auth', 'User', 'Bots', 'Templates', 'Media', 
    'VisualEditor', 'Admin', 'System', 'exceptions', 'network'
]

# Версия SDK
__version__ = '0.1.1'