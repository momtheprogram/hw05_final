from django.db import models

from django.contrib.auth import get_user_model

User = get_user_model()


class Post(models.Model):
    text = models.TextField(
        help_text="Заполнение данного поля является обязательным",
        verbose_name="Текст поста",
    )
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    group = models.ForeignKey(
        'Group',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        help_text="Выбрать группу (не обязательно)",
        verbose_name="Группа"
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
    )

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ['-pub_date']
        default_related_name = 'posts'


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=50, null=False, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    text = models.TextField(
        help_text="Напишите комментарий",
        verbose_name="Комментарий",
    )
    created = models.DateTimeField(
        "Время добавления комментария",
        auto_now_add=True,
    )

    class Meta:
        default_related_name = 'comments'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )
