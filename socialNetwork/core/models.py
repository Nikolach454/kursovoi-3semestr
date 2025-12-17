from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class City(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    country = models.CharField(max_length=100, default='Россия', verbose_name='Страна')

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'
        ordering = ['name']

    def __str__(self):
        return f"{self.name}, {self.country}"


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Название')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'
        ordering = ['name']

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    GENDER_CHOICES = [
        ('M', 'Мужской'),
        ('F', 'Женский'),
        ('O', 'Другой'),
    ]

    email = models.EmailField(unique=True, verbose_name='Email')
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    username = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name='Имя пользователя')
    avatar_url = models.CharField(max_length=500, blank=True, null=True, verbose_name='URL аватара')
    bio = models.TextField(blank=True, null=True, verbose_name='О себе')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Телефон')
    city = models.ForeignKey(City, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Город')
    birth_date = models.DateField(blank=True, null=True, verbose_name='Дата рождения')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True, verbose_name='Пол')
    is_online = models.BooleanField(default=False, verbose_name='Онлайн')
    last_seen = models.DateTimeField(blank=True, null=True, verbose_name='Последнее посещение')
    is_verified = models.BooleanField(default=False, verbose_name='Верифицирован')
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Роль')
    is_staff = models.BooleanField(default=False, verbose_name='Сотрудник')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    created_by = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, related_name='users_created', verbose_name='Создал')
    updated_by = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, related_name='users_updated', verbose_name='Обновил')

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class Community(models.Model):
    TYPE_CHOICES = [
        ('open', 'Открытое'),
        ('closed', 'Закрытое'),
    ]

    name = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    avatar_url = models.CharField(max_length=500, blank=True, null=True, verbose_name='URL аватара')
    cover_url = models.CharField(max_length=500, blank=True, null=True, verbose_name='URL обложки')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='open', verbose_name='Тип')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_communities', verbose_name='Владелец')
    members_count = models.PositiveIntegerField(default=0, verbose_name='Количество участников')
    is_verified = models.BooleanField(default=False, verbose_name='Верифицировано')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='communities_created', verbose_name='Создал')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='communities_updated', verbose_name='Обновил')

    class Meta:
        verbose_name = 'Сообщество'
        verbose_name_plural = 'Сообщества'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', verbose_name='Автор')
    community = models.ForeignKey(Community, on_delete=models.CASCADE, blank=True, null=True, related_name='posts', verbose_name='Сообщество')
    content = models.TextField(verbose_name='Содержание')
    views_count = models.PositiveIntegerField(default=0, verbose_name='Количество просмотров')
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='posts_created', verbose_name='Создал')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='posts_updated', verbose_name='Обновил')

    class Meta:
        verbose_name = 'Публикация'
        verbose_name_plural = 'Публикации'
        ordering = ['-created_at']

    def __str__(self):
        return f"Пост от {self.author.get_full_name()} ({self.created_at.strftime('%d.%m.%Y')})"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name='Публикация')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name='Автор')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='replies', verbose_name='Родительский комментарий')
    content = models.TextField(verbose_name='Содержание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='comments_created', verbose_name='Создал')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='comments_updated', verbose_name='Обновил')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-created_at']

    def __str__(self):
        return f"Комментарий от {self.author.get_full_name()} к посту #{self.post.id}"


class Chat(models.Model):
    TYPE_CHOICES = [
        ('private', 'Приватный'),
        ('group', 'Групповой'),
    ]

    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='private', verbose_name='Тип')
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name='Название')
    avatar_url = models.CharField(max_length=500, blank=True, null=True, verbose_name='URL аватара')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='chats_created', verbose_name='Создал')

    class Meta:
        verbose_name = 'Чат'
        verbose_name_plural = 'Чаты'
        ordering = ['-updated_at']

    def __str__(self):
        if self.name:
            return self.name
        return f"Чат #{self.id} ({self.get_type_display()})"


class Message(models.Model):
    STATUS_CHOICES = [
        ('sent', 'Отправлено'),
        ('delivered', 'Доставлено'),
        ('read', 'Прочитано'),
    ]

    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages', verbose_name='Чат')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', verbose_name='Отправитель')
    content = models.TextField(verbose_name='Содержание')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='sent', verbose_name='Статус')
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, related_name='replies', verbose_name='Ответ на')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='messages_created', verbose_name='Создал')

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['created_at']

    def __str__(self):
        return f"Сообщение от {self.sender.get_full_name()} в {self.chat}"


class Media(models.Model):
    TYPE_CHOICES = [
        ('image', 'Изображение'),
        ('video', 'Видео'),
        ('audio', 'Аудио'),
        ('document', 'Документ'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='media_files', verbose_name='Владелец')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='image', verbose_name='Тип')
    url = models.CharField(max_length=500, verbose_name='URL')
    thumbnail_url = models.CharField(max_length=500, blank=True, null=True, verbose_name='URL миниатюры')
    mime_type = models.CharField(max_length=100, blank=True, null=True, verbose_name='MIME тип')
    size = models.BigIntegerField(blank=True, null=True, verbose_name='Размер (байты)')
    original_name = models.CharField(max_length=255, blank=True, null=True, verbose_name='Оригинальное имя')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True, null=True, related_name='media_files', verbose_name='Публикация')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, blank=True, null=True, related_name='media_files', verbose_name='Сообщение')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='media_created', verbose_name='Создал')

    class Meta:
        verbose_name = 'Медиафайл'
        verbose_name_plural = 'Медиафайлы'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_type_display()} - {self.original_name or self.url}"


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes', verbose_name='Пользователь')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True, null=True, related_name='likes', verbose_name='Публикация')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, blank=True, null=True, related_name='likes', verbose_name='Комментарий')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Лайк'
        verbose_name_plural = 'Лайки'
        ordering = ['-created_at']
        unique_together = [['user', 'post'], ['user', 'comment']]

    def __str__(self):
        if self.post:
            return f"{self.user.get_full_name()} лайкнул пост #{self.post.id}"
        elif self.comment:
            return f"{self.user.get_full_name()} лайкнул комментарий #{self.comment.id}"
        return f"Лайк от {self.user.get_full_name()}"


class Friendship(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидание'),
        ('accepted', 'Принято'),
        ('declined', 'Отклонено'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friendships_initiated', verbose_name='Пользователь')
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friendships_received', verbose_name='Друг')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='friendships_created', verbose_name='Создал')

    class Meta:
        verbose_name = 'Дружба'
        verbose_name_plural = 'Дружба'
        ordering = ['-created_at']
        unique_together = ['user', 'friend']

    def __str__(self):
        return f"{self.user.get_full_name()} и {self.friend.get_full_name()} ({self.get_status_display()})"


class UserCommunity(models.Model):
    ROLE_CHOICES = [
        ('member', 'Участник'),
        ('moderator', 'Модератор'),
        ('admin', 'Администратор'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_memberships', verbose_name='Пользователь')
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='members', verbose_name='Сообщество')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member', verbose_name='Роль')
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата вступления')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='user_communities_created', verbose_name='Создал')

    class Meta:
        verbose_name = 'Участие в сообществе'
        verbose_name_plural = 'Участия в сообществах'
        ordering = ['-joined_at']
        unique_together = ['user', 'community']

    def __str__(self):
        return f"{self.user.get_full_name()} в {self.community.name} ({self.get_role_display()})"


class ChatParticipant(models.Model):
    ROLE_CHOICES = [
        ('member', 'Участник'),
        ('admin', 'Администратор'),
    ]

    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='participants', verbose_name='Чат')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_participations', verbose_name='Пользователь')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member', verbose_name='Роль')
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата вступления')
    last_read_at = models.DateTimeField(blank=True, null=True, verbose_name='Последнее прочтение')

    class Meta:
        verbose_name = 'Участник чата'
        verbose_name_plural = 'Участники чатов'
        ordering = ['-joined_at']
        unique_together = ['chat', 'user']

    def __str__(self):
        return f"{self.user.get_full_name()} в {self.chat}"
