# Ответы на вопросы по Django и REST

## Django

### 1. MVC и MTV в Django

**MVC (Model-View-Controller):**
- Model — данные и бизнес-логика
- View — отображение данных (UI)
- Controller — обработка запросов, связь Model и View

**MTV (Model-Template-View) в Django:**
- **Model** — модели данных (`models.py`)
- **Template** — HTML-шаблоны (`templates/`)
- **View** — обработка запросов и логика (`views.py`)

**Отличие:** В Django "View" выполняет роль Controller, а "Template" — роль View из MVC.

**Пример из проекта:**
```python
# Model (models.py)
class Post(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)

# View (views.py)
def index(request):
    posts = Post.objects.filter(is_published=True)
    return render(request, 'core/index.html', {'latest_posts': posts})

# Template (index.html)
{% for post in latest_posts %}
    <div>{{ post.content }}</div>
{% endfor %}
```

---

### 2. CSRF (Cross-Site Request Forgery)

**Что это:** Атака, при которой злоумышленник заставляет пользователя выполнить нежелательное действие на сайте, где он авторизован.

**Защита в Django:**
- `{% csrf_token %}` — токен в формах
- `CsrfViewMiddleware` — middleware для проверки
- `@csrf_protect` — декоратор для view
- `@csrf_exempt` — отключение проверки (осторожно!)

**Пример:**
```html
<form method="post">
    {% csrf_token %}
    <input type="text" name="content">
    <button type="submit">Отправить</button>
</form>
```

---

### 3. Возврат данных клиенту

**Способы:**
```python
from django.http import JsonResponse
from rest_framework.response import Response

# Django
return JsonResponse({'status': 'ok', 'data': data})

# DRF
return Response({'status': 'ok'}, status=status.HTTP_200_OK)
```

**Статусы ответов:**

| Группа | Значение | Примеры |
|--------|----------|---------|
| 2xx | Успех | 200 OK, 201 Created, 204 No Content |
| 3xx | Перенаправление | 301 Moved Permanently, 302 Found, 304 Not Modified |
| 4xx | Ошибка клиента | 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found |
| 5xx | Ошибка сервера | 500 Internal Server Error, 502 Bad Gateway, 503 Service Unavailable |

---

### 4. Middleware

**Что это:** Промежуточный слой, обрабатывающий запросы/ответы до и после view.

**Для чего:** Аутентификация, логирование, CORS, сжатие, обработка сессий.

**Реализация:**
```python
class SimpleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Код ДО view
        print(f"Request: {request.path}")

        response = self.get_response(request)

        # Код ПОСЛЕ view
        print(f"Response: {response.status_code}")
        return response
```

**Регистрация в settings.py:**
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'myapp.middleware.SimpleMiddleware',  # свой middleware
]
```

---

### 5. GET и POST запросы

| GET | POST |
|-----|------|
| Получение данных | Отправка/изменение данных |
| Параметры в URL | Параметры в теле запроса |
| Кэшируется | Не кэшируется |
| Ограничение длины URL | Нет ограничений |
| Безопасный (idempotent) | Небезопасный |

**Пример:**
```python
def my_view(request):
    if request.method == 'GET':
        search = request.GET.get('search', '')  # ?search=text
        return render(request, 'search.html')

    elif request.method == 'POST':
        content = request.POST.get('content')
        Post.objects.create(content=content, author=request.user)
        return redirect('index')
```

---

### 6. select_related и prefetch_related

**select_related** — JOIN для ForeignKey/OneToOne (один запрос):
```python
# Без оптимизации: N+1 запросов
posts = Post.objects.all()
for post in posts:
    print(post.author.email)  # каждый раз новый запрос

# С select_related: 1 запрос с JOIN
posts = Post.objects.select_related('author').all()
```

**prefetch_related** — отдельные запросы для ManyToMany/reverse FK:
```python
# Загрузить посты со всеми комментариями (2 запроса)
posts = Post.objects.prefetch_related('comments').all()
```

**Разница:**
- `select_related` — SQL JOIN, для "одиночных" связей
- `prefetch_related` — отдельный запрос, для "множественных" связей

---

### 7. Meta в классах Django

**Что это:** Внутренний класс для метаданных модели/формы/сериализатора.

**В моделях:**
```python
class Post(models.Model):
    content = models.TextField()

    class Meta:
        db_table = 'posts'           # имя таблицы
        ordering = ['-created_at']   # сортировка по умолчанию
        verbose_name = 'Пост'        # название в админке
        verbose_name_plural = 'Посты'
        unique_together = ['author', 'title']  # уникальность
        indexes = [models.Index(fields=['created_at'])]
```

**В сериализаторах:**
```python
class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'content', 'author']
        read_only_fields = ['id', 'created_at']
```

---

### 8. Админ-панель: настройка и регистрация

**Файл:** `admin.py`

**Регистрация модели (из проекта):**
```python
from django.contrib import admin
from .models import Post, Community, User

# Простая регистрация
admin.site.register(City)

# С настройками
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'content_preview', 'created_at')
```

---

### 9. Админ-панель: list_display, list_filter, fieldsets

**Из проекта (`admin.py`):**
```python
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # Колонки в списке
    list_display = ('id', 'email', 'get_full_name_display', 'city', 'is_online', 'role')

    # Фильтры справа
    list_filter = ('is_staff', 'is_active', 'is_verified', 'gender', 'role', 'city')

    # Группировка полей в форме редактирования
    fieldsets = (
        ('Основная информация', {
            'fields': ('email', 'password', 'first_name', 'last_name')
        }),
        ('Профиль', {
            'fields': ('avatar', 'bio', 'phone', 'city', 'birth_date')
        }),
        ('Права доступа', {
            'fields': ('is_active', 'is_staff', 'is_superuser')
        }),
    )
```

---

### 10. Админ-панель: inlines

**Что это:** Встроенные формы связанных моделей.

**Из проекта:**
```python
class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0  # не показывать пустые формы
    fk_name = 'post'

class MediaInline(admin.TabularInline):
    model = Media
    extra = 0

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    inlines = [CommentInline, MediaInline, LikeInline]
```

**Типы:** `TabularInline` (таблица), `StackedInline` (вертикально)

---

### 11. raw_id_fields

**Что это:** Замена выпадающего списка на поле ввода ID с поиском.

**Зачем:** Когда связанных объектов много (тысячи), выпадающий список тормозит.

**Из проекта:**
```python
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    raw_id_fields = ('author', 'community', 'created_by', 'updated_by')
```

Вместо `<select>` с 10000 пользователей — поле ID с кнопкой поиска.

---

### 12. login, logout, get_user_model

```python
from django.contrib.auth import login, logout, get_user_model

# get_user_model — получить модель пользователя
User = get_user_model()
user = User.objects.get(email='test@example.com')

# login — авторизовать пользователя
def login_view(request):
    user = authenticate(email=email, password=password)
    if user:
        login(request, user)  # создает сессию
        return redirect('index')

# logout — выйти из системы
def logout_view(request):
    logout(request)  # удаляет сессию
    return redirect('login')
```

---

## REST Framework

### 1. Что такое REST

**REST (Representational State Transfer)** — архитектурный стиль API.

**Принципы:**
- Клиент-сервер
- Stateless (без состояния)
- Единообразный интерфейс (URL = ресурс)
- Кэширование

**HTTP методы:**
| Метод | CRUD | Пример |
|-------|------|--------|
| GET | Read | GET /api/posts/ |
| POST | Create | POST /api/posts/ |
| PUT/PATCH | Update | PUT /api/posts/1/ |
| DELETE | Delete | DELETE /api/posts/1/ |

---

### 2. Отличия ViewSet, GenericViewSet, ModelViewSet, APIView

| Класс | Описание | Методы |
|-------|----------|--------|
| **APIView** | Базовый класс, ручная реализация | get(), post(), put(), delete() |
| **ViewSet** | Группировка действий | list(), create(), retrieve(), update(), destroy() |
| **GenericViewSet** | ViewSet + миксины | + get_queryset(), get_serializer() |
| **ModelViewSet** | Полный CRUD из коробки | Всё готово, только указать model и serializer |

**Пример из проекта:**
```python
class PostViewSet(viewsets.ModelViewSet):  # всё готово
    queryset = Post.objects.all()
    serializer_class = PostSerializer
```

---

### 3-4. @detail_route, @list_route, @action

**@detail_route и @list_route** — устаревшие (Django < 2.0).

**@action** — современная замена:
```python
from rest_framework.decorators import action

class PostViewSet(viewsets.ModelViewSet):

    # list_route → action(detail=False)
    @action(detail=False, methods=['get'])
    def published(self, request):
        """GET /api/posts/published/"""
        posts = self.queryset.filter(is_published=True)
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

    # detail_route → action(detail=True)
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """POST /api/posts/1/like/"""
        post = self.get_object()
        Like.objects.create(post=post, user=request.user)
        return Response({'status': 'liked'})
```

---

### 5. Автоматический роутинг (register)

```python
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

# register(prefix, viewset, basename)
router.register(r'posts', PostViewSet, basename='post')
router.register(r'communities', CommunityViewSet, basename='community')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('api/', include(router.urls)),
]
```

**Автоматически создаются URL:**
- GET/POST `/api/posts/`
- GET/PUT/DELETE `/api/posts/{id}/`
- GET `/api/posts/published/` (для @action)

---

### 6. Сериализаторы

**Что это:** Преобразование данных между Python-объектами и JSON.

**Зачем:** Валидация, сериализация (объект → JSON), десериализация (JSON → объект).

**Типы полей:**
```python
class PostSerializer(serializers.ModelSerializer):
    # Автоматические поля из модели
    # + кастомные:
    author_name = serializers.SerializerMethodField()  # вычисляемое
    likes_count = serializers.IntegerField(read_only=True)
    content = serializers.CharField(max_length=5000)

    class Meta:
        model = Post
        fields = ['id', 'content', 'author', 'author_name', 'likes_count']

    def get_author_name(self, obj):
        return obj.author.get_full_name()
```

---

### 7. Сериализаторы: Meta, extra_kwargs

**extra_kwargs** — дополнительные настройки для полей:
```python
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'first_name']
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 8},
            'email': {'required': True},
            'first_name': {'max_length': 50}
        }
```

---

### 8. Сериализаторы: validators

**Из проекта (`serializers.py`):**
```python
class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'content', 'author']

    def validate_content(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Содержание поста должно быть не менее 10 символов"
            )

        forbidden_words = ['спам', 'реклама']
        for word in forbidden_words:
            if word in value.lower():
                raise serializers.ValidationError(f"Запрещенное слово: {word}")

        return value

    def validate(self, data):
        # Валидация нескольких полей
        if data.get('community') and not data['community'].members.filter(user=self.context['request'].user).exists():
            raise serializers.ValidationError("Вы не участник сообщества")
        return data
```

---

### 9. reverse и reverse_lazy

**reverse** — получение URL по имени маршрута:
```python
from django.urls import reverse, reverse_lazy

# reverse — вычисляется сразу
url = reverse('core:post_detail', kwargs={'pk': 1})
# Результат: '/posts/1/'

# reverse_lazy — вычисляется при обращении (для class-based views)
class PostCreateView(CreateView):
    success_url = reverse_lazy('core:index')
```

**Пример в консоли:**
```python
>>> from django.urls import reverse
>>> reverse('core:index')
'/'
>>> reverse('core:user_profile', kwargs={'user_id': 1})
'/profile/1/'
>>> reverse('core:chat_detail', args=[5])
'/chats/5/'
```

---

### 10. get_serializer_context

**Что это:** Метод, передающий контекст в сериализатор.

**По умолчанию передает:** `request`, `view`, `format`.

```python
class PostViewSet(viewsets.ModelViewSet):

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        context['is_admin'] = self.request.user.is_staff
        return context

# В сериализаторе:
class PostSerializer(serializers.ModelSerializer):
    def validate(self, data):
        user = self.context.get('user')  # доступ к контексту
        request = self.context.get('request')

        if not user.is_verified:
            raise serializers.ValidationError("Только верифицированные пользователи")
        return data
```
