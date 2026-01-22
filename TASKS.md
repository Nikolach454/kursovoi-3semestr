# Выполненные задания

## Оценка "3" (удовлетворительно)

### 1. REST API на Django REST Framework для 2+ моделей
- **Реализация:** [core/api_views.py](socialNetwork/core/api_views.py)
- **Сериализаторы:** [core/serializers.py](socialNetwork/core/serializers.py)
- **URL маршруты:** [core/urls.py](socialNetwork/core/urls.py) (строки 5-10)
- Модели: `Post`, `Community`, `User`, `Comment`

### 2. Q-запросы (минимум 1)
- **Реализация:** [core/api_views.py](socialNetwork/core/api_views.py)
- `PostViewSet.get_queryset()` - строки 20-35
- `CommunityViewSet.get_queryset()` - строки 55-65

### 3. Пагинация
- **Реализация:** [socialNetwork/settings.py](socialNetwork/socialNetwork/settings.py) - строки 130-135
- Настроен `PageNumberPagination` с размером страницы 10

### 4. Фильтрация с django-filter
- **Реализация:** [core/filters.py](socialNetwork/core/filters.py)
- Фильтры: `PostFilter`, `CommunityFilter`, `UserFilter`, `CommentFilter`
- **Применение:** [core/api_views.py](socialNetwork/core/api_views.py) - `filterset_class`

### 5. Отслеживание истории изменений (django-simple-history)
- **Модели:** [core/models.py](socialNetwork/core/models.py)
- Поля `history` в моделях `User`, `Post`, `Community`
- **Админка:** [core/admin.py](socialNetwork/core/admin.py) - `SimpleHistoryAdmin`

### 6. Экспорт данных в Excel (django-import-export)
- **Ресурсы:** [core/resources.py](socialNetwork/core/resources.py)
- `PostResource`, `CommunityResource`, `UserResource`, `CommentResource`
- **Админка:** [core/admin.py](socialNetwork/core/admin.py) - `ImportExportModelAdmin`

### 7. Management-команды
- **cleanup_inactive_users:** [core/management/commands/cleanup_inactive_users.py](socialNetwork/core/management/commands/cleanup_inactive_users.py)
- **populate_test_data:** [core/management/commands/populate_test_data.py](socialNetwork/core/management/commands/populate_test_data.py)

### 8. Декоратор @action в ViewSet
- **Реализация:** [core/api_views.py](socialNetwork/core/api_views.py)
- `PostViewSet.my_posts()` - строка 37
- `PostViewSet.published()` - строка 44
- `CommunityViewSet.my_communities()` - строка 75
- `UserViewSet.me()` - строка 95
- `UserViewSet.online()` - строка 100

### 9. Настройка админ-панели
- **Реализация:** [core/admin.py](socialNetwork/core/admin.py)
- `list_display` - отображаемые поля
- `list_filter` - фильтры в боковой панели
- `search_fields` - поля для поиска
- `fieldsets` - группировка полей
- `inlines` - встроенные формы
- `raw_id_fields` - выбор связанных объектов
- `date_hierarchy` - навигация по датам

---

## Оценка "4" (хорошо)

### 10. Несколько Q-запросов с OR, AND, NOT
- **Реализация:** [core/api_views.py](socialNetwork/core/api_views.py)
- **OR запрос:** `PostViewSet.get_queryset()` - строки 25-30
  ```python
  Q(content__icontains=search) | Q(author__first_name__icontains=search) | Q(author__last_name__icontains=search)
  ```
- **AND запрос:** `CommunityViewSet.get_queryset()` - строки 60-63
  ```python
  Q(name__icontains=search) & Q(is_verified=True)
  ```
- **NOT запрос:** [core/views.py](socialNetwork/core/views.py) - функция `get_user_friends()`
  ```python
  Q(user=user, status='accepted') | Q(friend=user, status='accepted')
  ```

### 11. Линтер (flake8/ruff)
- **Конфигурация flake8:** [.flake8](socialNetwork/.flake8)
- **Конфигурация ruff:** [pyproject.toml](socialNetwork/pyproject.toml) - секция `[tool.ruff]`

---

## Оценка "5" (отлично)

### 12. Docker и docker-compose
- **Dockerfile:** [Dockerfile](socialNetwork/Dockerfile)
- **docker-compose.yml:** [docker-compose.yml](socialNetwork/docker-compose.yml)
- **Переменные окружения:** [.env.docker](socialNetwork/.env.docker)
- **Docker ignore:** [.dockerignore](socialNetwork/.dockerignore)

### 13. Фильтрация по 5+ полям
- **Реализация:** [core/filters.py](socialNetwork/core/filters.py)

**PostFilter (6 полей):**
- `author` - по автору
- `community` - по сообществу
- `is_published` - по статусу публикации
- `created_at_after` - дата создания от
- `created_at_before` - дата создания до
- `content` - по содержанию

**CommunityFilter (5 полей):**
- `type` - тип сообщества
- `is_verified` - верификация
- `owner` - владелец
- `name` - название
- `created_at_after` - дата создания от

**UserFilter (6 полей):**
- `city` - город
- `gender` - пол
- `is_online` - онлайн статус
- `is_verified` - верификация
- `role` - роль
- `search` - поиск по имени/email

---

## Дополнительный функционал социальной сети

### Друзья
- **Views:** [core/views.py](socialNetwork/core/views.py) - `friends_list`, `add_friend`, `accept_friend`, `decline_friend`, `remove_friend`
- **Шаблон:** [core/templates/core/friends_list.html](socialNetwork/core/templates/core/friends_list.html)

### Личные сообщения
- **Views:** [core/views.py](socialNetwork/core/views.py) - `chats_list`, `chat_detail`, `create_chat`
- **Шаблоны:** [core/templates/core/chats_list.html](socialNetwork/core/templates/core/chats_list.html), [core/templates/core/chat_detail.html](socialNetwork/core/templates/core/chat_detail.html)

### Групповые чаты
- **View:** [core/views.py](socialNetwork/core/views.py) - `create_group_chat`
- **Шаблон:** [core/templates/core/create_group_chat.html](socialNetwork/core/templates/core/create_group_chat.html)

### Сообщества
- **Views:** [core/views.py](socialNetwork/core/views.py) - `community_list`, `community_detail`, `join_community`, `leave_community`
- **Шаблоны:** [core/templates/core/community_list.html](socialNetwork/core/templates/core/community_list.html), [core/templates/core/community_detail.html](socialNetwork/core/templates/core/community_detail.html)

### Профиль пользователя
- **View:** [core/views.py](socialNetwork/core/views.py) - `user_profile`
- **Шаблон:** [core/templates/core/user_profile.html](socialNetwork/core/templates/core/user_profile.html)
