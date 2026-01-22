from django_filters import rest_framework as filters
from django.db.models import Q
from .models import Post, Community, User, Comment


class PostFilter(filters.FilterSet):
    author_id = filters.NumberFilter(field_name='author__id')
    community_id = filters.NumberFilter(field_name='community__id')
    is_published = filters.BooleanFilter(field_name='is_published')
    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    min_views = filters.NumberFilter(field_name='views_count', lookup_expr='gte')
    search = filters.CharFilter(method='filter_search')

    class Meta:
        model = Post
        fields = ['author_id', 'community_id', 'is_published', 'created_after', 'created_before', 'min_views']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(content__icontains=value) |
            Q(author__first_name__icontains=value) |
            Q(author__last_name__icontains=value)
        )


class CommunityFilter(filters.FilterSet):
    type = filters.ChoiceFilter(choices=[('open', 'Open'), ('closed', 'Closed')])
    is_verified = filters.BooleanFilter(field_name='is_verified')
    min_members = filters.NumberFilter(field_name='members_count', lookup_expr='gte')
    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    search = filters.CharFilter(method='filter_search')

    class Meta:
        model = Community
        fields = ['type', 'is_verified', 'min_members', 'created_after']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) | Q(description__icontains=value)
        )


class UserFilter(filters.FilterSet):
    is_verified = filters.BooleanFilter(field_name='is_verified')
    is_online = filters.BooleanFilter(field_name='is_online')
    gender = filters.ChoiceFilter(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
    city_id = filters.NumberFilter(field_name='city__id')
    search = filters.CharFilter(method='filter_search')

    class Meta:
        model = User
        fields = ['is_verified', 'is_online', 'gender', 'city_id']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(first_name__icontains=value) |
            Q(last_name__icontains=value) |
            Q(email__icontains=value)
        )


class CommentFilter(filters.FilterSet):
    post_id = filters.NumberFilter(field_name='post__id')
    author_id = filters.NumberFilter(field_name='author__id')
    has_parent = filters.BooleanFilter(field_name='parent', lookup_expr='isnull', exclude=True)
    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')

    class Meta:
        model = Comment
        fields = ['post_id', 'author_id', 'has_parent', 'created_after']
