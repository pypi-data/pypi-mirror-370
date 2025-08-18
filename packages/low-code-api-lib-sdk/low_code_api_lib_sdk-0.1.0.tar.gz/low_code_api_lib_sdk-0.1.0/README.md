# My SDK

SDK для работы с API платформы.

## Установка

```bash
pip install my_sdk
```

## Использование

### Инициализация клиента

```python
from my_sdk import Client

# Создание клиента с токеном авторизации
client = Client(token="ваш_токен_авторизации")
```

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

## Лицензия

MIT