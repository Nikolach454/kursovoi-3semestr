from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Posts
    path('posts/', views.post_list, name='post_list'),
    path('posts/create/', views.post_create, name='post_create'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('posts/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    path('posts/<int:post_id>/delete/', views.post_delete, name='post_delete'),
    path('posts/<int:post_id>/like/', views.toggle_like, name='toggle_like'),
    path('posts/<int:post_id>/comment/', views.add_comment, name='add_comment'),

    # Users & Profiles
    path('users/<int:user_id>/', views.user_profile, name='user_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),

    # Friends
    path('friends/', views.friends_list, name='friends_list'),
    path('users/<int:user_id>/add-friend/', views.add_friend, name='add_friend'),
    path('users/<int:user_id>/remove-friend/', views.remove_friend, name='remove_friend'),
    path('friendship/<int:friendship_id>/accept/', views.accept_friend, name='accept_friend'),
    path('friendship/<int:friendship_id>/decline/', views.decline_friend, name='decline_friend'),
    path('friendship/<int:friendship_id>/cancel/', views.cancel_friend_request, name='cancel_friend_request'),

    # Chats & Messages
    path('chats/', views.chats_list, name='chats_list'),
    path('chats/<int:chat_id>/', views.chat_detail, name='chat_detail'),
    path('chats/create/<int:user_id>/', views.create_chat, name='create_chat'),
    path('chats/create-group/', views.create_group_chat, name='create_group_chat'),

    # Communities
    path('communities/', views.community_list, name='community_list'),
    path('communities/<int:community_id>/', views.community_detail, name='community_detail'),
    path('communities/<int:community_id>/join/', views.join_community, name='join_community'),
    path('communities/<int:community_id>/leave/', views.leave_community, name='leave_community'),
]
