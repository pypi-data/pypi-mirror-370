# Low Code API Lib SDK

**Версия 0.1.1** - Мощный SDK для работы с API платформы Low Code с расширенными возможностями обработки ошибок, сетевого взаимодействия и тестирования.

## 🚀 Новое в версии 0.1.1

- ✅ **Расширенная обработка ошибок** - специализированные исключения для различных типов ошибок
- ✅ **Сетевые возможности** - NetworkManager для управления соединениями и NetworkSharing для обмена данными
- ✅ **Модули тестирования** - полный набор тестов для всех компонентов SDK
- ✅ **Улучшенная документация** - подробная документация в папке `docs/`
- ✅ **Повышенная надежность** - автоматические повторные попытки и пулинг соединений

## 📦 Установка

```bash
pip install low-code-api-lib-sdk
```

### Требования

- Python 3.7+
- requests >= 2.25.0
- urllib3 >= 1.26.0

## 📖 Использование

### Быстрый старт

```python
from my_sdk import Client
from my_sdk.exceptions import SDKError, AuthenticationError

# Создание клиента с токеном авторизации
client = Client(
    token="ваш_токен_авторизации",
    base_url="https://api.lowcodeapi.ru"  # опционально
)

# Безопасное использование с обработкой ошибок
try:
    user_info = client.auth.get_me()
    print(f"Добро пожаловать, {user_info['name']}!")
except AuthenticationError as e:
    print(f"Ошибка аутентификации: {e}")
except SDKError as e:
    print(f"Ошибка SDK: {e}")
```

### 🔧 Инициализация клиента

### Аутентификация

```python
# Получение модуля аутентификации
auth = client.auth()

# Вход в систему
login_result = auth.login(username="username", password="password")
print(login_result)

# Регистрация нового пользователя
register_result = auth.register(
    username="new_user", 
    password="secure_password", 
    email="user@example.com"
)
print(register_result)

# Выход из системы
logout_result = auth.logout()
print(logout_result)
```

### Работа с пользователями

```python
# Получение модуля пользователя
user = client.user()

# Получение информации о пользователе
user_info = user.get_info()
print(user_info)

# Получение статистики пользователя
user_stats = user.get_stats()
print(user_stats)
```

### Работа с ботами

```python
# Получение модуля ботов
bots = client.bots()

# Генерация кода бота
generate_code_result = bots.generate_code(bot_id=123, language="python")
print(generate_code_result)

# Запуск бота
run_bot_result = bots.run_bot(bot_id=123)
print(run_bot_result)

# Остановка бота
stop_bot_result = bots.stop_bot(bot_id=123)
print(stop_bot_result)

# Получение статуса бота
bot_status = bots.get_bot_status(bot_id=123)
print(bot_status)
```

### Работа с шаблонами

```python
# Получение модуля шаблонов
templates = client.templates()

# Скачивание шаблона
download_result = templates.download(template_id=456)
print(download_result)

# Оценка шаблона
rate_result = templates.rate(template_id=456, rating=5)
print(rate_result)

# Добавление комментария к шаблону
comment_result = templates.comment(template_id=456, comment_text="Отличный шаблон!")
print(comment_result)

# Использование шаблона для создания бота
use_template_result = templates.use_template(template_id=456, bot_name="Мой новый бот")
print(use_template_result)
```

### Работа с медиафайлами

```python
# Получение модуля медиа
media = client.media()

# Загрузка медиафайла для бота
with open("image.jpg", "rb") as file:
    upload_result = media.upload_media(bot_id=123, file_data=file)
print(upload_result)
```

### Работа с визуальным редактором

```python
# Получение модуля визуального редактора
visual_editor = client.visual_editor()

# Получение конфигурации блоков
blocks_config = visual_editor.get_blocks_config()
print(blocks_config)

# Генерация кода из блоков
blocks = [
    {"type": "start", "id": "1"},
    {"type": "message", "id": "2", "text": "Привет, мир!"}
]
generate_code_result = visual_editor.generate_code(blocks=blocks)
print(generate_code_result)
```

### Административные функции

```python
# Получение модуля администратора
admin = client.admin()

# Получение статистики для администратора
admin_stats = admin.get_stats()
print(admin_stats)

# Получение комплексной статистики платформы
comprehensive_stats = admin.get_comprehensive_stats()
print(comprehensive_stats)
```

### Системные функции

```python
# Получение модуля системы
system = client.system()

# Проверка работоспособности системы
health_check = system.health_check()
print(health_check)
```

## 🌐 Сетевые возможности (Новое в 0.1.1)

### NetworkManager для управления соединениями

```python
from my_sdk.network import get_network_manager

# Получение менеджера сети с автоматическими повторными попытками
network_manager = get_network_manager()

# Выполнение запроса с автоматическими повторами
response = network_manager.request(
    method='GET',
    url='https://api.example.com/data',
    max_retries=3,
    timeout=30
)
```

### NetworkSharing для обмена данными

```python
from my_sdk.network import NetworkSharing

# Создание сервера для обмена данными
sharing = NetworkSharing()

# Запуск сервера
sharing.start_server(host='localhost', port=8080)

# Отправка данных клиенту
data = {'message': 'Привет от сервера!'}
sharing.send_data('client_id', data)

# Подключение клиента
client_sharing = NetworkSharing()
client_sharing.connect_client('localhost', 8080)
```

## ⚠️ Обработка ошибок (Новое в 0.1.1)

### Специализированные исключения

```python
from my_sdk.exceptions import (
    SDKError, AuthenticationError, NetworkError, 
    ValidationError, RateLimitError
)

try:
    # Ваш код здесь
    result = client.users.get_user(user_id=123)
except AuthenticationError:
    print("Проблемы с аутентификацией")
except NetworkError:
    print("Проблемы с сетью")
except ValidationError as e:
    print(f"Ошибка валидации: {e}")
except RateLimitError:
    print("Превышен лимит запросов")
except SDKError as e:
    print(f"Общая ошибка SDK: {e}")
```

### Валидация входных данных

```python
from my_sdk.exceptions import validate_token, validate_base_url

# Валидация токена
try:
    validate_token("your_token_here")
except ValidationError as e:
    print(f"Неверный токен: {e}")

# Валидация URL
try:
    validate_base_url("https://api.example.com")
except ValidationError as e:
    print(f"Неверный URL: {e}")
```

## 🧪 Тестирование (Новое в 0.1.1)

### Запуск тестов

```bash
# Установка зависимостей для тестирования
pip install pytest pytest-cov

# Запуск всех тестов
pytest tests/

# Запуск тестов с покрытием кода
pytest tests/ --cov=my_sdk --cov-report=html

# Запуск конкретного теста
pytest tests/test_client.py::TestClient::test_client_initialization
```

### Структура тестов

- `tests/test_base.py` - тесты базового API класса
- `tests/test_client.py` - тесты клиента SDK
- `tests/test_exceptions.py` - тесты обработки ошибок
- `tests/test_network.py` - тесты сетевых возможностей

## 📚 Документация

Полная документация доступна в папке `docs/`:

- `docs/API_REFERENCE.md` - справочник по API
- `docs/EXAMPLES.md` - примеры использования
- `docs/GITHUB_ACTIONS_PUBLISH.md` - публикация через GitHub Actions
- `docs/PUBLISH.md` - руководство по публикации

## 🔧 Разработка

### Установка для разработки

```bash
# Клонирование репозитория
git clone <repository_url>
cd My_SDK_API_LIB_PIP

# Установка в режиме разработки
pip install -e .

# Установка зависимостей для разработки
pip install pytest pytest-cov black flake8
```

### Запуск линтеров

```bash
# Форматирование кода
black my_sdk/ tests/

# Проверка стиля кода
flake8 my_sdk/ tests/
```

## 📝 Changelog

### v0.1.1 (Текущая версия)
- Добавлена расширенная обработка ошибок
- Добавлены сетевые возможности (NetworkManager, NetworkSharing)
- Добавлены модули тестирования
- Улучшена документация
- Добавлена валидация входных данных
- Добавлен пулинг соединений

### v0.1.0
- Базовая функциональность SDK
- Поддержка основных API модулей
- Аутентификация и авторизация

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции (`git checkout -b feature/amazing-feature`)
3. Зафиксируйте изменения (`git commit -m 'Add amazing feature'`)
4. Отправьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

MIT