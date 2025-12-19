from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.urls import reverse
from django.contrib import messages
from .models import Post, User, Community
from .forms import PostForm


def index(request):
    latest_posts = Post.objects.filter(is_published=True).order_by('-created_at')[:10]
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
    context = {
        'post': post,
    }
    return render(request, 'core/post_detail.html', context)


def user_profile(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user_posts = Post.objects.filter(author=user, is_published=True).order_by('-created_at')
    context = {
        'profile_user': user,
        'user_posts': user_posts,
    }
    return render(request, 'core/user_profile.html', context)


def community_list(request):
    communities = Community.objects.all().order_by('-created_at')
    context = {
        'communities': communities,
    }
    return render(request, 'core/community_list.html', context)


def community_detail(request, community_id):
    community = get_object_or_404(Community, pk=community_id)
    community_posts = Post.objects.filter(community=community, is_published=True).order_by('-created_at')
    context = {
        'community': community,
        'community_posts': community_posts,
    }
    return render(request, 'core/community_detail.html', context)


def post_create(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Вы должны войти в систему, чтобы создать публикацию.')
        return redirect('core:index')

    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.created_by = request.user
            post.save()
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
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.updated_by = request.user
            post.save()
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
