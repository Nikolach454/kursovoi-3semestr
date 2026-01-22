from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Post, User, Community, Friendship, Like, Comment, Chat, ChatParticipant, Message, Media, UserCommunity
from .forms import PostForm, UserRegistrationForm, UserLoginForm


def index(request):
    if request.user.is_authenticated:
        if request.method == 'POST' and 'quick_post' in request.POST:
            content = request.POST.get('content', '').strip()
            if content:
                post = Post.objects.create(
                    author=request.user,
                    content=content,
                    is_published=True,
                    created_by=request.user
                )
                images = request.FILES.getlist('images')
                for image in images:
                    Media.objects.create(
                        owner=request.user,
                        type='image',
                        file=image,
                        original_name=image.name,
                        size=image.size,
                        post=post,
                        created_by=request.user
                    )
                messages.success(request, 'Пост опубликован!')
                return redirect('core:index')

    posts_list = Post.objects.filter(is_published=True).select_related('author').prefetch_related('media_files', 'likes', 'comments').order_by('-created_at')

    # Пагинация
    paginator = Paginator(posts_list, 10)  # 10 постов на страницу
    page_number = request.GET.get('page')
    latest_posts = paginator.get_page(page_number)

    context = {
        'latest_posts': latest_posts,
    }
    return render(request, 'core/index.html', context)


def post_list(request):
    posts = Post.objects.filter(is_published=True).order_by('-created_at')
    context = {
        'posts': posts,
    }
    return render(request, 'core/post_list.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post.views_count += 1
    post.save()
    comments = post.comments.filter(parent__isnull=True).select_related('author').prefetch_related('replies__author')
    context = {
        'post': post,
        'comments': comments,
    }
    return render(request, 'core/post_detail.html', context)


def get_user_friends(user):
    friend_ids = set()
    friendships = Friendship.objects.filter(
        Q(user=user, status='accepted') | Q(friend=user, status='accepted')
    )
    for f in friendships:
        if f.user == user:
            friend_ids.add(f.friend_id)
        else:
            friend_ids.add(f.user_id)
    return User.objects.filter(id__in=friend_ids)


def user_profile(request, user_id):
    profile_user = get_object_or_404(User, pk=user_id)
    user_posts = Post.objects.filter(author=profile_user, is_published=True).select_related('author').prefetch_related('media_files', 'likes', 'comments').order_by('-created_at')

    friends = get_user_friends(profile_user)
    friends_count = friends.count()

    communities_count = UserCommunity.objects.filter(user=profile_user).count()

    friendship_status = None
    pending_friendship_id = None

    if request.user.is_authenticated and request.user != profile_user:
        friendship = Friendship.objects.filter(
            Q(user=request.user, friend=profile_user) | Q(user=profile_user, friend=request.user)
        ).first()

        if friendship:
            if friendship.status == 'accepted':
                friendship_status = 'accepted'
            elif friendship.status == 'pending':
                if friendship.user == request.user:
                    friendship_status = 'pending_sent'
                else:
                    friendship_status = 'pending_received'
                    pending_friendship_id = friendship.id

    context = {
        'profile_user': profile_user,
        'user_posts': user_posts,
        'friends': friends[:6],
        'friends_count': friends_count,
        'communities_count': communities_count,
        'friendship_status': friendship_status,
        'pending_friendship_id': pending_friendship_id,
    }
    return render(request, 'core/user_profile.html', context)


@login_required
def edit_profile(request):
    if request.method == 'POST':
        user = request.user

        # Обновление аватара
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']

        # Обновление текстовых полей
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.bio = request.POST.get('bio', user.bio)
        user.phone = request.POST.get('phone', user.phone)

        # Обновление даты рождения
        birth_date = request.POST.get('birth_date')
        if birth_date:
            user.birth_date = birth_date

        # Обновление пола
        gender = request.POST.get('gender')
        if gender in ['M', 'F', 'O', '']:
            user.gender = gender if gender else None

        user.save()
        messages.success(request, 'Профиль успешно обновлен!')
        return redirect('core:user_profile', user_id=user.id)

    return render(request, 'core/edit_profile.html')


def community_list(request):
    communities = Community.objects.all().select_related('owner').order_by('-created_at')
    context = {
        'communities': communities,
    }
    return render(request, 'core/community_list.html', context)


def community_detail(request, community_id):
    community = get_object_or_404(Community, pk=community_id)
    community_posts = Post.objects.filter(community=community, is_published=True).select_related('author').prefetch_related('media_files', 'likes', 'comments').order_by('-created_at')

    is_member = False
    user_role = None
    if request.user.is_authenticated:
        membership = UserCommunity.objects.filter(user=request.user, community=community).first()
        if membership:
            is_member = True
            user_role = membership.role

    members = UserCommunity.objects.filter(community=community).select_related('user')[:10]

    context = {
        'community': community,
        'community_posts': community_posts,
        'is_member': is_member,
        'user_role': user_role,
        'members': members,
    }
    return render(request, 'core/community_detail.html', context)


@login_required
def join_community(request, community_id):
    community = get_object_or_404(Community, pk=community_id)

    if community.type == 'closed':
        messages.error(request, 'Это закрытое сообщество')
        return redirect('core:community_detail', community_id=community_id)

    membership, created = UserCommunity.objects.get_or_create(
        user=request.user,
        community=community,
        defaults={'created_by': request.user}
    )

    if created:
        community.members_count += 1
        community.save(update_fields=['members_count'])
        messages.success(request, f'Вы вступили в сообщество "{community.name}"')
    else:
        messages.info(request, 'Вы уже состоите в этом сообществе')

    return redirect('core:community_detail', community_id=community_id)


@login_required
def leave_community(request, community_id):
    community = get_object_or_404(Community, pk=community_id)

    if community.owner == request.user:
        messages.error(request, 'Владелец не может покинуть сообщество')
        return redirect('core:community_detail', community_id=community_id)

    membership = UserCommunity.objects.filter(user=request.user, community=community).first()
    if membership:
        membership.delete()
        community.members_count = max(0, community.members_count - 1)
        community.save(update_fields=['members_count'])
        messages.success(request, f'Вы покинули сообщество "{community.name}"')
    else:
        messages.info(request, 'Вы не состоите в этом сообществе')

    return redirect('core:community_detail', community_id=community_id)


def post_create(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Вы должны войти в систему, чтобы создать публикацию.')
        return redirect('core:index')

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.created_by = request.user
            post.save()

            images = request.FILES.getlist('images')
            for image in images:
                Media.objects.create(
                    owner=request.user,
                    type='image',
                    file=image,
                    original_name=image.name,
                    size=image.size,
                    post=post,
                    created_by=request.user
                )

            messages.success(request, 'Публикация успешно создана!')
            return redirect('core:post_detail', post_id=post.id)
    else:
        form = PostForm()

    context = {
        'form': form,
        'action': 'create',
    }
    return render(request, 'core/post_form.html', context)


def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if not request.user.is_authenticated or post.author != request.user:
        messages.error(request, 'У вас нет прав для редактирования этой публикации.')
        return redirect('core:post_detail', post_id=post.id)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.updated_by = request.user
            post.save()

            images = request.FILES.getlist('images')
            for image in images:
                Media.objects.create(
                    owner=request.user,
                    type='image',
                    file=image,
                    original_name=image.name,
                    size=image.size,
                    post=post,
                    created_by=request.user
                )

            messages.success(request, 'Публикация успешно обновлена!')
            return redirect('core:post_detail', post_id=post.id)
    else:
        form = PostForm(instance=post)

    context = {
        'form': form,
        'post': post,
        'action': 'edit',
    }
    return render(request, 'core/post_form.html', context)


def post_delete(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if not request.user.is_authenticated or post.author != request.user:
        messages.error(request, 'У вас нет прав для удаления этой публикации.')
        return redirect('core:post_detail', post_id=post.id)

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Публикация успешно удалена!')
        return redirect('core:post_list')

    context = {
        'post': post,
    }
    return render(request, 'core/post_confirm_delete.html', context)


def register(request):
    if request.user.is_authenticated:
        return redirect('core:index')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.get_full_name()}! Вы успешно зарегистрировались.')
            return redirect('core:index')
    else:
        form = UserRegistrationForm()

    context = {
        'form': form,
    }
    return render(request, 'core/register.html', context)


def user_login(request):
    if request.user.is_authenticated:
        return redirect('core:index')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {user.get_full_name()}!')
                next_url = request.GET.get('next', 'core:index')
                return redirect(next_url)
    else:
        form = UserLoginForm()

    context = {
        'form': form,
    }
    return render(request, 'core/login.html', context)


def user_logout(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('core:index')


@login_required
def friends_list(request):
    tab = request.GET.get('tab', 'friends')

    friends = get_user_friends(request.user)
    friends_count = friends.count()

    pending_requests = Friendship.objects.filter(friend=request.user, status='pending').select_related('user')
    pending_requests_count = pending_requests.count()

    outgoing_requests = Friendship.objects.filter(user=request.user, status='pending').select_related('friend')

    search_query = request.GET.get('q', '')
    search_results = []
    friend_ids = list(friends.values_list('id', flat=True))
    pending_sent_ids = list(outgoing_requests.values_list('friend_id', flat=True))

    if tab == 'search' and search_query:
        search_results = User.objects.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        ).exclude(id=request.user.id)[:20]

    context = {
        'tab': tab,
        'friends': friends,
        'friends_count': friends_count,
        'pending_requests': pending_requests,
        'pending_requests_count': pending_requests_count,
        'outgoing_requests': outgoing_requests,
        'search_query': search_query,
        'search_results': search_results,
        'friend_ids': friend_ids,
        'pending_sent_ids': pending_sent_ids,
    }
    return render(request, 'core/friends_list.html', context)


@login_required
def add_friend(request, user_id):
    friend = get_object_or_404(User, pk=user_id)
    if friend == request.user:
        messages.error(request, 'Нельзя добавить себя в друзья')
        return redirect('core:user_profile', user_id=user_id)

    existing = Friendship.objects.filter(
        Q(user=request.user, friend=friend) | Q(user=friend, friend=request.user)
    ).first()

    if existing:
        messages.info(request, 'Заявка уже отправлена или вы уже друзья')
    else:
        Friendship.objects.create(
            user=request.user,
            friend=friend,
            status='pending',
            created_by=request.user
        )
        messages.success(request, f'Заявка в друзья отправлена пользователю {friend.get_full_name()}')

    return redirect('core:user_profile', user_id=user_id)


@login_required
def accept_friend(request, friendship_id):
    friendship = get_object_or_404(Friendship, pk=friendship_id, friend=request.user, status='pending')
    friendship.status = 'accepted'
    friendship.save()
    messages.success(request, f'Вы теперь друзья с {friendship.user.get_full_name()}')
    return redirect('core:friends_list')


@login_required
def decline_friend(request, friendship_id):
    friendship = get_object_or_404(Friendship, pk=friendship_id, friend=request.user, status='pending')
    friendship.status = 'declined'
    friendship.save()
    messages.info(request, 'Заявка отклонена')
    return redirect('core:friends_list')


@login_required
def cancel_friend_request(request, friendship_id):
    friendship = get_object_or_404(Friendship, pk=friendship_id, user=request.user, status='pending')
    friendship.delete()
    messages.info(request, 'Заявка отменена')
    return redirect('core:friends_list')


@login_required
def remove_friend(request, user_id):
    friend = get_object_or_404(User, pk=user_id)
    Friendship.objects.filter(
        Q(user=request.user, friend=friend) | Q(user=friend, friend=request.user)
    ).delete()
    messages.success(request, f'{friend.get_full_name()} удален из друзей')
    return redirect('core:user_profile', user_id=user_id)


@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    like = Like.objects.filter(user=request.user, post=post).first()

    if like:
        like.delete()
        liked = False
    else:
        Like.objects.create(user=request.user, post=post)
        liked = True

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'liked': liked, 'count': post.likes.count()})

    return redirect('core:index')


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        parent_id = request.POST.get('parent_id')
        if content:
            parent = None
            if parent_id:
                parent = Comment.objects.filter(id=parent_id, post=post).first()
            Comment.objects.create(
                post=post,
                author=request.user,
                content=content,
                parent=parent,
                created_by=request.user
            )
            messages.success(request, 'Комментарий добавлен')
    return redirect('core:post_detail', post_id=post_id)


@login_required
def chats_list(request):
    user_chats = Chat.objects.filter(
        participants__user=request.user
    ).distinct().prefetch_related(
        'participants__user', 'messages'
    ).order_by('-updated_at')

    context = {
        'chats': user_chats,
    }
    return render(request, 'core/chats_list.html', context)


@login_required
def chat_detail(request, chat_id):
    chat = get_object_or_404(Chat, pk=chat_id)
    if not ChatParticipant.objects.filter(chat=chat, user=request.user).exists():
        messages.error(request, 'У вас нет доступа к этому чату')
        return redirect('core:chats_list')

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        images = request.FILES.getlist('images')

        if content or images:
            message = Message.objects.create(
                chat=chat,
                sender=request.user,
                content=content,
                created_by=request.user
            )

            for image in images:
                Media.objects.create(
                    owner=request.user,
                    type='image',
                    file=image,
                    original_name=image.name,
                    size=image.size,
                    message=message,
                    created_by=request.user
                )

            chat.save()
            return redirect('core:chat_detail', chat_id=chat_id)

    messages_list = chat.messages.select_related('sender').prefetch_related('media_files').order_by('created_at')

    context = {
        'chat': chat,
        'messages': messages_list,
    }
    return render(request, 'core/chat_detail.html', context)


@login_required
def create_chat(request, user_id):
    other_user = get_object_or_404(User, pk=user_id)

    existing_chat = Chat.objects.filter(
        type='private',
        participants__user=request.user
    ).filter(
        participants__user=other_user
    ).first()

    if existing_chat:
        return redirect('core:chat_detail', chat_id=existing_chat.id)

    chat = Chat.objects.create(
        type='private',
        created_by=request.user
    )
    ChatParticipant.objects.create(chat=chat, user=request.user)
    ChatParticipant.objects.create(chat=chat, user=other_user)

    return redirect('core:chat_detail', chat_id=chat.id)


@login_required
def create_group_chat(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        member_ids = request.POST.getlist('members')

        if not name:
            messages.error(request, 'Введите название группы')
            return redirect('core:friends_list')

        chat = Chat.objects.create(
            type='group',
            name=name,
            created_by=request.user
        )

        ChatParticipant.objects.create(chat=chat, user=request.user, role='admin')

        for member_id in member_ids:
            try:
                member = User.objects.get(id=member_id)
                ChatParticipant.objects.create(chat=chat, user=member)
            except User.DoesNotExist:
                pass

        messages.success(request, f'Групповой чат "{name}" создан')
        return redirect('core:chat_detail', chat_id=chat.id)

    friends = get_user_friends(request.user)
    context = {
        'friends': friends,
    }
    return render(request, 'core/create_group_chat.html', context)
