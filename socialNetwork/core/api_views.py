from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from django.utils import timezone
from .models import Post, Community, User, Comment, Like, UserCommunity
from .serializers import PostSerializer, CommunitySerializer, CommentSerializer
from .filters import PostFilter, CommunityFilter, CommentFilter


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PostFilter
    search_fields = ['content', 'author__first_name', 'author__last_name']
    ordering_fields = ['created_at', 'views_count', 'updated_at']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Post.objects.filter(is_published=True)

        author_id = self.request.query_params.get('author_id')
        if author_id:
            queryset = queryset.filter(author_id=author_id)

        community_id = self.request.query_params.get('community_id')
        if community_id:
            queryset = queryset.filter(community_id=community_id)

        return queryset.select_related('author', 'community').prefetch_related('likes', 'comments')

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            created_by=self.request.user
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(methods=['GET'], detail=False)
    def popular(self, request):
        posts = Post.objects.filter(is_published=True).annotate(
            total_likes=Count('likes'),
            total_comments=Count('comments')
        ).order_by('-total_likes', '-total_comments')[:10]

        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

    @action(methods=['GET'], detail=False)
    def trending(self, request):
        from datetime import timedelta
        week_ago = timezone.now() - timedelta(days=7)

        posts = Post.objects.filter(
            is_published=True,
            created_at__gte=week_ago
        ).annotate(
            engagement=Count('likes') + Count('comments') + Count('views_count')
        ).order_by('-engagement')[:10]

        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

    @action(methods=['POST'], detail=True)
    def like(self, request, pk=None):
        post = self.get_object()
        user = request.user

        if not user.is_authenticated:
            return Response(
                {'error': 'Необходимо авторизоваться'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        like_obj, created = Like.objects.get_or_create(
            user=user,
            post=post
        )

        if created:
            return Response(
                {'message': 'Лайк добавлен', 'likes_count': post.likes.count()},
                status=status.HTTP_201_CREATED
            )
        else:
            like_obj.delete()
            return Response(
                {'message': 'Лайк удален', 'likes_count': post.likes.count()},
                status=status.HTTP_200_OK
            )

    @action(methods=['POST'], detail=True)
    def increment_views(self, request, pk=None):
        post = self.get_object()
        post.views_count += 1
        post.save(update_fields=['views_count'])

        return Response(
            {'views_count': post.views_count},
            status=status.HTTP_200_OK
        )

    @action(methods=['POST'], detail=True)
    def publish(self, request, pk=None):
        post = self.get_object()

        if post.author != request.user:
            return Response(
                {'error': 'Только автор может публиковать пост'},
                status=status.HTTP_403_FORBIDDEN
            )

        post.is_published = True
        post.save(update_fields=['is_published'])

        return Response(
            {'message': 'Пост опубликован'},
            status=status.HTTP_200_OK
        )

    @action(methods=['POST'], detail=True)
    def unpublish(self, request, pk=None):
        post = self.get_object()

        if post.author != request.user:
            return Response(
                {'error': 'Только автор может снять публикацию'},
                status=status.HTTP_403_FORBIDDEN
            )

        post.is_published = False
        post.save(update_fields=['is_published'])

        return Response(
            {'message': 'Пост снят с публикации'},
            status=status.HTTP_200_OK
        )

    @action(methods=['GET'], detail=False)
    def advanced_search(self, request):
        from datetime import timedelta

        min_views = request.query_params.get('min_views', 10)
        week_ago = timezone.now() - timedelta(days=7)

        posts = Post.objects.filter(
            (Q(views_count__gte=min_views) | Q(likes__isnull=False)) &
            Q(is_published=True) &
            ~Q(community__isnull=True) &
            Q(created_at__gte=week_ago)
        ).distinct().select_related('author', 'community')[:20]

        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)


class CommunityViewSet(viewsets.ModelViewSet):
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CommunityFilter
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'members_count', 'name']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Community.objects.all()

        community_type = self.request.query_params.get('type')
        if community_type:
            queryset = queryset.filter(type=community_type)

        is_verified = self.request.query_params.get('is_verified')
        if is_verified:
            queryset = queryset.filter(is_verified=is_verified.lower() == 'true')

        return queryset.select_related('owner').prefetch_related('members', 'posts')

    def perform_create(self, serializer):
        serializer.save(
            owner=self.request.user,
            created_by=self.request.user
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(methods=['GET'], detail=False)
    def popular(self, request):
        communities = Community.objects.annotate(
            total_members=Count('members')
        ).order_by('-total_members')[:10]

        serializer = self.get_serializer(communities, many=True)
        return Response(serializer.data)

    @action(methods=['GET'], detail=False)
    def search(self, request):
        query = request.query_params.get('q', '')

        if not query:
            return Response(
                {'error': 'Параметр поиска q обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )

        communities = Community.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )[:20]

        serializer = self.get_serializer(communities, many=True)
        return Response(serializer.data)

    @action(methods=['POST'], detail=True)
    def join(self, request, pk=None):
        community = self.get_object()
        user = request.user

        if not user.is_authenticated:
            return Response(
                {'error': 'Необходимо авторизоваться'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if community.type == 'closed':
            return Response(
                {'error': 'Это закрытое сообщество, требуется приглашение'},
                status=status.HTTP_403_FORBIDDEN
            )

        membership, created = UserCommunity.objects.get_or_create(
            user=user,
            community=community,
            defaults={'created_by': user}
        )

        if created:
            community.members_count += 1
            community.save(update_fields=['members_count'])

            return Response(
                {'message': 'Вы вступили в сообщество', 'members_count': community.members_count},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'message': 'Вы уже являетесь участником этого сообщества'},
                status=status.HTTP_200_OK
            )

    @action(methods=['POST'], detail=True)
    def leave(self, request, pk=None):
        community = self.get_object()
        user = request.user

        if not user.is_authenticated:
            return Response(
                {'error': 'Необходимо авторизоваться'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if community.owner == user:
            return Response(
                {'error': 'Владелец не может покинуть сообщество'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            membership = UserCommunity.objects.get(user=user, community=community)
            membership.delete()

            community.members_count = max(0, community.members_count - 1)
            community.save(update_fields=['members_count'])

            return Response(
                {'message': 'Вы покинули сообщество', 'members_count': community.members_count},
                status=status.HTTP_200_OK
            )
        except UserCommunity.DoesNotExist:
            return Response(
                {'error': 'Вы не являетесь участником этого сообщества'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(methods=['GET'], detail=True)
    def members(self, request, pk=None):
        community = self.get_object()
        memberships = UserCommunity.objects.filter(community=community).select_related('user')

        members_data = [{
            'user_id': m.user.id,
            'full_name': m.user.get_full_name(),
            'role': m.role,
            'joined_at': m.joined_at
        } for m in memberships]

        return Response(members_data)

    @action(methods=['GET'], detail=True)
    def posts(self, request, pk=None):
        community = self.get_object()
        posts = Post.objects.filter(
            community=community,
            is_published=True
        ).select_related('author')[:20]

        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    @action(methods=['GET'], detail=False)
    def recommended(self, request):
        from datetime import timedelta

        month_ago = timezone.now() - timedelta(days=30)

        communities = Community.objects.filter(
            (Q(is_verified=True) | Q(members_count__gte=50)) &
            Q(type='open') &
            ~Q(owner__is_active=False) &
            Q(created_at__gte=month_ago)
        ).annotate(
            total_members=Count('members')
        ).order_by('-total_members')[:15]

        serializer = self.get_serializer(communities, many=True)
        return Response(serializer.data)
