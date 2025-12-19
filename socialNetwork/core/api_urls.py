from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import PostViewSet, CommunityViewSet

router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')
router.register(r'communities', CommunityViewSet, basename='community')

urlpatterns = [
    path('', include(router.urls)),
]
