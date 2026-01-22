from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, DateTimeWidget
from .models import Post, Community, User, Comment


class PostResource(resources.ModelResource):
    author_full_name = fields.Field(column_name='Author Full Name')
    community_name = fields.Field(column_name='Community')
    likes_count = fields.Field(column_name='Likes')
    comments_count = fields.Field(column_name='Comments')
    created_at = fields.Field(
        column_name='Created At',
        attribute='created_at',
        widget=DateTimeWidget(format='%d.%m.%Y %H:%M')
    )

    class Meta:
        model = Post
        fields = ('id', 'author_full_name', 'community_name', 'content', 'views_count', 'likes_count', 'comments_count', 'is_published', 'created_at')
        export_order = ('id', 'author_full_name', 'community_name', 'content', 'views_count', 'likes_count', 'comments_count', 'is_published', 'created_at')

    def dehydrate_author_full_name(self, post):
        return post.author.get_full_name() if post.author else ''

    def dehydrate_community_name(self, post):
        return post.community.name if post.community else 'Personal Post'

    def dehydrate_likes_count(self, post):
        return post.likes.count()

    def dehydrate_comments_count(self, post):
        return post.comments.count()

    def get_export_queryset(self, queryset):
        return queryset.filter(is_published=True).select_related('author', 'community').prefetch_related('likes', 'comments')


class CommunityResource(resources.ModelResource):
    owner_name = fields.Field(column_name='Owner')
    type_display = fields.Field(column_name='Type')
    created_at = fields.Field(
        column_name='Created At',
        attribute='created_at',
        widget=DateTimeWidget(format='%d.%m.%Y %H:%M')
    )

    class Meta:
        model = Community
        fields = ('id', 'name', 'description', 'type_display', 'owner_name', 'members_count', 'is_verified', 'created_at')
        export_order = ('id', 'name', 'description', 'type_display', 'owner_name', 'members_count', 'is_verified', 'created_at')

    def dehydrate_owner_name(self, community):
        return community.owner.get_full_name() if community.owner else ''

    def dehydrate_type_display(self, community):
        return community.get_type_display()

    def get_export_queryset(self, queryset):
        return queryset.select_related('owner').order_by('-members_count')


class UserResource(resources.ModelResource):
    full_name = fields.Field(column_name='Full Name')
    city_name = fields.Field(column_name='City')
    gender_display = fields.Field(column_name='Gender')
    created_at = fields.Field(
        column_name='Registered At',
        attribute='created_at',
        widget=DateTimeWidget(format='%d.%m.%Y %H:%M')
    )

    class Meta:
        model = User
        fields = ('id', 'email', 'full_name', 'username', 'phone', 'city_name', 'gender_display', 'is_verified', 'is_online', 'created_at')
        export_order = ('id', 'email', 'full_name', 'username', 'phone', 'city_name', 'gender_display', 'is_verified', 'is_online', 'created_at')

    def dehydrate_full_name(self, user):
        return user.get_full_name()

    def dehydrate_city_name(self, user):
        return str(user.city) if user.city else ''

    def dehydrate_gender_display(self, user):
        return user.get_gender_display() if user.gender else ''

    def get_export_queryset(self, queryset):
        return queryset.select_related('city').filter(is_active=True)


class CommentResource(resources.ModelResource):
    author_name = fields.Field(column_name='Author')
    post_preview = fields.Field(column_name='Post')
    created_at = fields.Field(
        column_name='Created At',
        attribute='created_at',
        widget=DateTimeWidget(format='%d.%m.%Y %H:%M')
    )

    class Meta:
        model = Comment
        fields = ('id', 'author_name', 'post_preview', 'content', 'created_at')
        export_order = ('id', 'author_name', 'post_preview', 'content', 'created_at')

    def dehydrate_author_name(self, comment):
        return comment.author.get_full_name() if comment.author else ''

    def dehydrate_post_preview(self, comment):
        if comment.post:
            content = comment.post.content
            return content[:50] + '...' if len(content) > 50 else content
        return ''

    def get_export_queryset(self, queryset):
        return queryset.select_related('author', 'post').order_by('-created_at')
