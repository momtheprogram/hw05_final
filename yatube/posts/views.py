# импорты не по зуз8
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from django.shortcuts import render, get_object_or_404, redirect

from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm


def index(request):
    post_list = Post.objects.all().select_related('author') # стоит также сделать связь с `group`, чтобы избежать лишних хинтов в БД
    page_obj = paginator(request, post_list)
    title = 'Главная страница сайта Yatube' # Не стоит превращать view в передачу статичных аргументов в шаблон. Используй `block title` для переопределения нужного блока. https://docs.djangoproject.com/en/4.0/ref/templates/language/#templates
    context = {
        'page_obj': page_obj,
        'title': title
    }
    template = 'posts/index.html' # Нет необходимости выносить в отдельную переменную template, можно сразу прокинуть шаблон в render() вторым аргументом- читабельность не потеряется.
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()[:10] # обрезка постов должна быть в отпагинированном объекте `page_obj`. Сейчас же в пагинацию не попадет никогда больше 10 постов группы
    page_obj = paginator(request, posts)
    context = {
        'group': group,
        'posts': posts, # вот это лишнее. Все объекты передаем в `page_obj`, отпагинированными.
        'page_obj': page_obj
    }
    template = 'posts/group_list.html'
    return render(request, template, context)


def profile(request, username):
    author = User.objects.get(username=username) # Используй `get_object_or_404(...)`, чтобы в случае отсутствия модели была 404 страничка. https://docs.djangoproject.com/en/4.0/topics/http/shortcuts/#get-object-or-404
    post_list = author.posts.all() # выборку принято называть с префиксом `queryset` `posts_queryset`, например. Тут же не список постов. Было бы здорово использовать `select_related`
    page_obj = paginator(request, post_list)
    title = f'Профайл пользователя {username}' # убрать в block tittle
    all_posts = post_list.count() # дай подходящий нейминг. тут хранится `количество` постов

    following = (
        request.user.is_authenticated
        and Follow.objects.filter( # выборка `Follow` должна проверять: подписан ли `текущий пользователь` на `автора`. Должно быть комплексное условие по двум полям
            author__following__user=request.user
        ).exists()
    )
    context = {
        'page_obj': page_obj,
        'title': title,
        'all_posts': all_posts,
        'author': author,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    posts_count = post.author.posts.count()
    context = {
        'title': post.text, # пост уже передается, не нужно отдельно вытягивать его атрибуты во вьюхе. Это можно сделать прямо в б=шаблоне
        'post_count': posts_count,
        'post': post,
        'comments': post.comments.all(),
        'form': CommentForm(),
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None,
                    files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=post.author)
    context = {
        'form': form,
        'is_edit': False # не обязательно передавать. Ошибки в шаблоне не будет, если переменной нет.
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    # Тут происходит лишний хинт в БД. Есть несколько вариантов избежать этого:
    #
    #  - Использовать `select_related`, подгружая нужные поля заранее;
    #  - Сравнивать не модели, а их `id` `request.user !=edit_post.author_id`
    #
    # https://docs.djangoproject.com/en/4.1/ref/models/querysets/#select-related
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'is_edit': True,
        'post': post
    }
    return render(request, 'posts/create_post.html', context)

# утилитам самое место в отдельном файле, например, `utils.py`. Во `views.py` только вьюхи
def paginator(request, posts):
    paginator = Paginator(posts, 10) # 10 вынеси в константу в settings.py, например
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


@login_required
def add_comment(request, post_id):
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, pk=post_id)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(
        author__following__user=request.user or None # or None в выборке никак не поможет. Тут формируется queryset, а не форма
    ).all()
    page_obj = paginator(request, post_list)
    return render(
        request,
        'posts/follow.html',
        context={'page_obj': page_obj,
                 }
    )


@login_required
def profile_follow(request, username):
    author = User.objects.get(username=username) # get_object_or_404
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username=author.username)


@login_required
def profile_unfollow(request, username):
    author = User.objects.get(username=username) # get_object_or_404
    following = Follow.objects.filter(user=request.user, author=author)
    if following: # exists(), чтобы просто проверить существование объектов, а не тянуть их из БД
        following.delete()
    return redirect('posts:profile', username=author.username)
