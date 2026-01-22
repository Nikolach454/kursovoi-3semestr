from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from import_export.admin import ImportExportModelAdmin
from simple_history.admin import SimpleHistoryAdmin
from .models import (
    City, Role, User, Community, Post, Comment, Chat, Message,
    Media, Like, Friendship, UserCommunity, ChatParticipant
)
from .resources import PostResource, CommunityResource, UserResource, CommentResource


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'country')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'country')
    list_filter = ('country',)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'description')


class UserCommunityInline(admin.TabularInline):
    model = UserCommunity
    extra = 0
    fk_name = 'user'
    raw_id_fields = ('community', 'created_by')
    readonly_fields = ('joined_at',)


class FriendshipInitiatedInline(admin.TabularInline):
    model = Friendship
    extra = 0
    fk_name = 'user'
    raw_id_fields = ('friend', 'created_by')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(User)
class UserAdmin(ImportExportModelAdmin, SimpleHistoryAdmin, BaseUserAdmin):
    resource_class = UserResource
    list_display = ('id', 'email', 'get_full_name_display', 'username', 'city', 'is_online_display', 'is_verified', 'role', 'is_staff', 'created_at')
    list_display_links = ('id', 'email')
    list_filter = ('is_staff', 'is_active', 'is_verified', 'is_online', 'gender', 'role', 'city')
    search_fields = ('email', 'first_name', 'last_name', 'username', 'phone')
    raw_id_fields = ('city', 'role', 'created_by', 'updated_by')
    readonly_fields = ('last_login', 'created_at', 'updated_at', 'last_seen')
    date_hierarchy = 'created_at'
    inlines = [UserCommunityInline, FriendshipInitiatedInline]

    fieldsets = (
        ('Основная информация', {
            'fields': ('email', 'password', 'first_name', 'last_name', 'username')
        }),
        ('Профиль', {
            'fields': ('avatar', 'bio', 'phone', 'city', 'birth_date', 'gender')
        }),
        ('Статус', {
            'fields': ('is_online', 'last_seen', 'is_verified', 'role')
        }),
        ('Права доступа', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Метаинформация', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by', 'last_login')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )

    ordering = ('-created_at',)

    @admin.display(description='Полное имя')
    def get_full_name_display(self, obj):
        return obj.get_full_name()

    @admin.display(description='Онлайн', boolean=True)
    def is_online_display(self, obj):
        return obj.is_online


class UserCommunityMemberInline(admin.TabularInline):
    model = UserCommunity
    extra = 0
    fk_name = 'community'
    raw_id_fields = ('user', 'created_by')
    readonly_fields = ('joined_at',)


class PostInline(admin.TabularInline):
    model = Post
    extra = 0
    fk_name = 'community'
    raw_id_fields = ('author', 'created_by', 'updated_by')
    readonly_fields = ('created_at', 'updated_at', 'views_count')
    fields = ('author', 'content', 'is_published', 'views_count')


@admin.register(Community)
class CommunityAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    resource_class = CommunityResource
    list_display = ('id', 'name', 'type', 'owner', 'members_count_display', 'is_verified', 'created_at')
    list_display_links = ('id', 'name')
    list_filter = ('type', 'is_verified', 'created_at')
    search_fields = ('name', 'description', 'owner__email', 'owner__first_name', 'owner__last_name')
    raw_id_fields = ('owner', 'created_by', 'updated_by')
    readonly_fields = ('created_at', 'updated_at', 'members_count')
    date_hierarchy = 'created_at'
    inlines = [UserCommunityMemberInline, PostInline]

    @admin.display(description='Участников')
    def members_count_display(self, obj):
        return obj.members_count


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fk_name = 'post'
    raw_id_fields = ('author', 'parent', 'created_by', 'updated_by')
    readonly_fields = ('created_at', 'updated_at')
    fields = ('author', 'content', 'parent')


class MediaInline(admin.TabularInline):
    model = Media
    extra = 0
    fk_name = 'post'
    raw_id_fields = ('owner', 'created_by')
    readonly_fields = ('created_at',)
    fields = ('owner', 'type', 'file', 'thumbnail', 'original_name')


class LikeInline(admin.TabularInline):
    model = Like
    extra = 0
    fk_name = 'post'
    raw_id_fields = ('user',)
    readonly_fields = ('created_at',)


@admin.register(Post)
class PostAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    resource_class = PostResource
    list_display = ('id', 'author', 'community', 'content_preview', 'views_count', 'likes_count_display', 'is_published', 'created_at')
    list_display_links = ('id', 'content_preview')
    list_filter = ('is_published', 'created_at', 'updated_at')
    search_fields = ('content', 'author__email', 'author__first_name', 'author__last_name', 'community__name')
    raw_id_fields = ('author', 'community', 'created_by', 'updated_by')
    readonly_fields = ('created_at', 'updated_at', 'views_count')
    date_hierarchy = 'created_at'
    inlines = [CommentInline, MediaInline, LikeInline]

    @admin.display(description='Содержание')
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content

    @admin.display(description='Лайков')
    def likes_count_display(self, obj):
        return obj.likes.count()


@admin.register(Comment)
class CommentAdmin(ImportExportModelAdmin):
    resource_class = CommentResource
    list_display = ('id', 'author', 'post', 'content_preview', 'parent', 'likes_count_display', 'created_at')
    list_display_links = ('id', 'content_preview')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('content', 'author__email', 'author__first_name', 'author__last_name')
    raw_id_fields = ('post', 'author', 'parent', 'created_by', 'updated_by')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'

    @admin.display(description='Содержание')
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content

    @admin.display(description='Лайков')
    def likes_count_display(self, obj):
        return obj.likes.count()


class ChatParticipantInline(admin.TabularInline):
    model = ChatParticipant
    extra = 0
    raw_id_fields = ('user',)
    readonly_fields = ('joined_at',)


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    fk_name = 'chat'
    raw_id_fields = ('sender', 'reply_to', 'created_by')
    readonly_fields = ('created_at', 'updated_at')
    fields = ('sender', 'content', 'status', 'reply_to')


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_or_id', 'type', 'participants_count_display', 'created_at', 'updated_at')
    list_display_links = ('id', 'name_or_id')
    list_filter = ('type', 'created_at', 'updated_at')
    search_fields = ('name',)
    raw_id_fields = ('created_by',)
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    inlines = [ChatParticipantInline, MessageInline]

    @admin.display(description='Название')
    def name_or_id(self, obj):
        return obj.name if obj.name else f"Чат #{obj.id}"

    @admin.display(description='Участников')
    def participants_count_display(self, obj):
        return obj.participants.count()


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'chat', 'content_preview', 'status', 'reply_to', 'created_at')
    list_display_links = ('id', 'content_preview')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('content', 'sender__email', 'sender__first_name', 'sender__last_name')
    raw_id_fields = ('chat', 'sender', 'reply_to', 'created_by')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'

    @admin.display(description='Содержание')
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'type', 'original_name', 'size_display', 'post', 'message', 'created_at')
    list_display_links = ('id', 'original_name')
    list_filter = ('type', 'created_at')
    search_fields = ('original_name', 'file', 'owner__email', 'owner__first_name', 'owner__last_name')
    raw_id_fields = ('owner', 'post', 'message', 'created_by')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'

    @admin.display(description='Размер')
    def size_display(self, obj):
        if not obj.size:
            return '-'
        size_kb = obj.size / 1024
        if size_kb < 1024:
            return f"{size_kb:.2f} KB"
        size_mb = size_kb / 1024
        return f"{size_mb:.2f} MB"


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post', 'comment', 'target_display', 'created_at')
    list_display_links = ('id', 'target_display')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    raw_id_fields = ('user', 'post', 'comment')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'

    @admin.display(description='Цель лайка')
    def target_display(self, obj):
        if obj.post:
            return f"Пост #{obj.post.id}"
        elif obj.comment:
            return f"Комментарий #{obj.comment.id}"
        return '-'


@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'friend', 'status', 'status_colored', 'created_at', 'updated_at')
    list_display_links = ('id', 'user')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'friend__email', 'friend__first_name', 'friend__last_name')
    raw_id_fields = ('user', 'friend', 'created_by')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'

    @admin.display(description='Статус')
    def status_colored(self, obj):
        colors = {
            'pending': '#FFA500',
            'accepted': '#28a745',
            'declined': '#dc3545'
        }
        color = colors.get(obj.status, '#000')
        return f'<span style="color: {color}; font-weight: bold;">{obj.get_status_display()}</span>'

    status_colored.allow_tags = True


@admin.register(UserCommunity)
class UserCommunityAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'community', 'role', 'joined_at')
    list_display_links = ('id', 'user')
    list_filter = ('role', 'joined_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'community__name')
    raw_id_fields = ('user', 'community', 'created_by')
    readonly_fields = ('joined_at',)
    date_hierarchy = 'joined_at'


@admin.register(ChatParticipant)
class ChatParticipantAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat', 'user', 'role', 'joined_at', 'last_read_at')
    list_display_links = ('id', 'user')
    list_filter = ('role', 'joined_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'chat__name')
    raw_id_fields = ('chat', 'user')
    readonly_fields = ('joined_at',)
    date_hierarchy = 'joined_at'
