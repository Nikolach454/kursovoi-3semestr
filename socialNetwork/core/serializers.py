from rest_framework import serializers
from .models import Post, Community, User, Comment


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'username',
                  'avatar_url', 'bio', 'phone', 'city', 'birth_date', 'gender',
                  'is_online', 'last_seen', 'is_verified', 'created_at']
        read_only_fields = ['id', 'is_verified', 'created_at']

    def get_full_name(self, obj):
        return obj.get_full_name()


class PostSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    community_name = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'author', 'author_name', 'community', 'community_name',
                  'content', 'views_count', 'is_published', 'created_at',
                  'updated_at', 'likes_count', 'comments_count']
        read_only_fields = ['id', 'author', 'views_count', 'created_at', 'updated_at']

    def get_author_name(self, obj):
        return obj.author.get_full_name()

    def get_community_name(self, obj):
        return obj.community.name if obj.community else None

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.count()

    def validate_content(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Содержание поста должно быть не менее 10 символов"
            )

        forbidden_words = ['спам', 'реклама', 'мошенничество']
        for word in forbidden_words:
            if word.lower() in value.lower():
                raise serializers.ValidationError(
                    f"Содержание поста содержит запрещенное слово: {word}"
                )

        return value

    def validate(self, data):
        if 'community' in data and data['community']:
            request = self.context.get('request')
            if request and request.user:
                user_is_member = data['community'].members.filter(user=request.user).exists()
                if not user_is_member and data['community'].owner != request.user:
                    raise serializers.ValidationError(
                        "Вы не можете публиковать посты в этом сообществе, так как не являетесь его участником"
                    )

        return data


class CommunitySerializer(serializers.ModelSerializer):
    owner_name = serializers.SerializerMethodField()
    posts_count = serializers.SerializerMethodField()

    class Meta:
        model = Community
        fields = ['id', 'name', 'description', 'avatar_url', 'cover_url', 'type',
                  'owner', 'owner_name', 'members_count', 'is_verified',
                  'created_at', 'updated_at', 'posts_count']
        read_only_fields = ['id', 'owner', 'members_count', 'is_verified',
                           'created_at', 'updated_at']

    def get_owner_name(self, obj):
        return obj.owner.get_full_name()

    def get_posts_count(self, obj):
        return obj.posts.count()

    def validate_name(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError(
                "Название сообщества должно быть не менее 3 символов"
            )

        if len(value) > 100:
            raise serializers.ValidationError(
                "Название сообщества не должно превышать 100 символов"
            )

        forbidden_words = ['админ', 'администрация', 'модератор', 'official']
        for word in forbidden_words:
            if word.lower() in value.lower():
                raise serializers.ValidationError(
                    f"Название сообщества не может содержать слово: {word}"
                )

        return value

    def validate_type(self, value):
        if value not in ['open', 'closed']:
            raise serializers.ValidationError(
                "Тип сообщества должен быть 'open' или 'closed'"
            )
        return value


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    replies_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'author_name', 'parent', 'content',
                  'created_at', 'updated_at', 'replies_count', 'likes_count']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']

    def get_author_name(self, obj):
        return obj.author.get_full_name()

    def get_replies_count(self, obj):
        return obj.replies.count()

    def get_likes_count(self, obj):
        return obj.likes.count()

    def validate_content(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError(
                "Комментарий должен быть не менее 2 символов"
            )
        return value
