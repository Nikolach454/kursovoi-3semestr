# Инструкция по демонстрации выполнения заданий

## Подготовка к демонстрации

### Запуск проекта локально

```bash
cd socialNetwork

# Установка зависимостей
pip install -r requirements.txt

# Применение миграций
python manage.py migrate

# Наполнение тестовыми данными
python manage.py populate_test_data

# Запуск сервера
python manage.py runserver
```

### Запуск через Docker

```bash
cd socialNetwork
docker-compose up --build
```

---

## Демонстрация заданий на "3"

### 1. REST API (Django REST Framework)

Открыть в браузере или Postman:

```
# Список постов
GET http://127.0.0.1:8000/api/posts/

# Список сообществ
GET http://127.0.0.1:8000/api/communities/

# Список пользователей
GET http://127.0.0.1:8000/api/users/

# Список комментариев
GET http://127.0.0.1:8000/api/comments/
```

**Что показать:** JSON-ответы с данными моделей, пагинация в ответе.

---

### 2. Q-запросы

```
# Поиск постов (Q-запрос с OR)
GET http://127.0.0.1:8000/api/posts/?search=привет

# Поиск сообществ (Q-запрос)
GET http://127.0.0.1:8000/api/communities/?search=программ
```

**Что показать:** Код в `api_views.py` строки 20-35, результаты поиска.

---

### 3. Пагинация

```
# Первая страница
GET http://127.0.0.1:8000/api/posts/

# Вторая страница
GET http://127.0.0.1:8000/api/posts/?page=2
```

**Что показать:** Поля `count`, `next`, `previous` в ответе, настройки в `settings.py`.

---

### 4. Фильтрация (django-filter)

```
# Фильтр по автору
GET http://127.0.0.1:8000/api/posts/?author=1

# Фильтр по сообществу
GET http://127.0.0.1:8000/api/posts/?community=1

# Фильтр опубликованных
GET http://127.0.0.1:8000/api/posts/?is_published=true

# Фильтр по дате
GET http://127.0.0.1:8000/api/posts/?created_at_after=2024-01-01

# Комбинированный фильтр
GET http://127.0.0.1:8000/api/posts/?is_published=true&author=1
```

**Что показать:** Файл `filters.py`, применение фильтров.

---

### 5. История изменений (django-simple-history)

1. Открыть админ-панель: http://127.0.0.1:8000/admin/
2. Войти: `admin` / `admin` (или создать суперпользователя)
3. Перейти в Посты → выбрать пост → изменить → сохранить
4. Нажать "История" в правом верхнем углу

**Что показать:** Вкладка "История" в админке, записи об изменениях.

---

### 6. Экспорт в Excel (django-import-export)

1. Открыть админ-панель: http://127.0.0.1:8000/admin/
2. Перейти в раздел "Посты" или "Сообщества"
3. Нажать кнопку "Экспорт" вверху списка
4. Выбрать формат (XLSX, CSV, JSON)
5. Нажать "Отправить"

**Что показать:** Кнопка экспорта, скачанный файл Excel.

---

### 7. Management-команды

```bash
# Команда очистки неактивных пользователей (режим проверки)
python manage.py cleanup_inactive_users --dry-run

# Команда с параметром дней
python manage.py cleanup_inactive_users --days=30 --dry-run

# Команда наполнения тестовыми данными
python manage.py populate_test_data

# Справка по команде
python manage.py cleanup_inactive_users --help
```

**Что показать:** Вывод команд, код в `management/commands/`.

---

### 8. Декоратор @action

```
# Мои посты (требует авторизации)
GET http://127.0.0.1:8000/api/posts/my_posts/

# Опубликованные посты
GET http://127.0.0.1:8000/api/posts/published/

# Мои сообщества
GET http://127.0.0.1:8000/api/communities/my_communities/

# Текущий пользователь
GET http://127.0.0.1:8000/api/users/me/

# Онлайн пользователи
GET http://127.0.0.1:8000/api/users/online/
```

**Что показать:** Код декораторов `@action` в `api_views.py`.

---

### 9. Настройка админ-панели

1. Открыть http://127.0.0.1:8000/admin/
2. Показать разделы:

**Пользователи:**
- Колонки: ID, Email, Полное имя, Город, Онлайн, Роль
- Фильтры справа: Статус, Верификация, Онлайн, Пол, Роль, Город
- Поиск по email, имени
- Группировка полей (fieldsets)
- Встроенные формы (inlines) - сообщества, друзья

**Посты:**
- Иерархия по датам (date_hierarchy)
- Встроенные комментарии, медиа, лайки

**Что показать:** Код в `admin.py`, интерфейс админки.

---

## Демонстрация заданий на "4"

### 10. Несколько Q-запросов с OR, AND, NOT

**Открыть файл `api_views.py` и показать:**

```python
# OR запрос (строки 25-30)
Q(content__icontains=search) | Q(author__first_name__icontains=search)

# AND запрос (строки 60-63)
Q(name__icontains=search) & Q(is_verified=True)
```

**Открыть файл `views.py` и показать:**
```python
# Запрос для поиска друзей
Q(user=user, status='accepted') | Q(friend=user, status='accepted')
```

**Тестирование:**
```
GET http://127.0.0.1:8000/api/posts/?search=день
GET http://127.0.0.1:8000/api/communities/?search=программ
```

---

### 11. Линтер

```bash
# Запуск flake8
flake8 core/

# Запуск ruff
ruff check core/

# Автоисправление с ruff
ruff check core/ --fix
```

**Что показать:** Конфигурации `.flake8` и `pyproject.toml`, вывод линтера.

---

## Демонстрация заданий на "5"

### 12. Docker

```bash
# Сборка и запуск
docker-compose up --build

# Проверка контейнеров
docker-compose ps

# Логи
docker-compose logs web
```

**Что показать:**
- Файл `Dockerfile` - многоэтапная сборка
- Файл `docker-compose.yml` - сервисы web и db
- Работающее приложение в контейнере

---

### 13. Фильтрация по 5+ полям

**Открыть файл `filters.py` и показать классы фильтров:**

**PostFilter (6 полей):**
```
GET http://127.0.0.1:8000/api/posts/?author=1
GET http://127.0.0.1:8000/api/posts/?community=2
GET http://127.0.0.1:8000/api/posts/?is_published=true
GET http://127.0.0.1:8000/api/posts/?created_at_after=2024-01-01
GET http://127.0.0.1:8000/api/posts/?created_at_before=2025-01-01
GET http://127.0.0.1:8000/api/posts/?content=привет
```

**CommunityFilter (5 полей):**
```
GET http://127.0.0.1:8000/api/communities/?type=open
GET http://127.0.0.1:8000/api/communities/?is_verified=true
GET http://127.0.0.1:8000/api/communities/?owner=1
GET http://127.0.0.1:8000/api/communities/?name=программ
GET http://127.0.0.1:8000/api/communities/?created_at_after=2024-01-01
```

**UserFilter (6 полей):**
```
GET http://127.0.0.1:8000/api/users/?city=1
GET http://127.0.0.1:8000/api/users/?gender=male
GET http://127.0.0.1:8000/api/users/?is_online=true
GET http://127.0.0.1:8000/api/users/?is_verified=true
GET http://127.0.0.1:8000/api/users/?role=1
GET http://127.0.0.1:8000/api/users/?search=иван
```

---

## Демонстрация функционала социальной сети

### Вход в систему
1. Открыть http://127.0.0.1:8000/
2. Нажать "Войти"
3. Ввести: `ivan@example.com` / `testpass123`

### Лента новостей
- URL: http://127.0.0.1:8000/
- Показать: создание поста, прикрепление фото, лайки

### Друзья
- URL: http://127.0.0.1:8000/friends/
- Вкладки: Все друзья, Заявки, Исходящие, Поиск
- Действия: принять/отклонить заявку, удалить друга

### Сообщения
- URL: http://127.0.0.1:8000/chats/
- Показать: список чатов, отправка сообщений, прикрепление фото
- Создание группового чата: http://127.0.0.1:8000/chats/create-group/

### Сообщества
- URL: http://127.0.0.1:8000/communities/
- Действия: вступить, выйти, просмотр участников

### Профиль
- URL: http://127.0.0.1:8000/profile/1/
- Показать: статистика, друзья, посты, кнопки действий

---

## Создание суперпользователя (если нужно)

```bash
python manage.py createsuperuser
# Email: admin@example.com
# Password: admin123
```

---

## Быстрая проверка всех требований

| Требование | Команда/URL для проверки |
|------------|--------------------------|
| REST API | `GET /api/posts/` |
| Q-запросы | `GET /api/posts/?search=текст` |
| Пагинация | `GET /api/posts/?page=2` |
| Фильтрация | `GET /api/posts/?author=1` |
| История | Админка → Посты → История |
| Excel экспорт | Админка → Посты → Экспорт |
| Management | `python manage.py cleanup_inactive_users --dry-run` |
| @action | `GET /api/posts/published/` |
| Админка | http://127.0.0.1:8000/admin/ |
| Q с OR/AND | Код в `api_views.py:25-30` |
| Линтер | `flake8 core/` |
| Docker | `docker-compose up --build` |
| 5+ фильтров | `filters.py` - PostFilter, UserFilter |
