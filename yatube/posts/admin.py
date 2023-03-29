from django.contrib import admin

from .models import Post, Group, Comment, Follow


class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author', 'group')
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


admin.site.register(Post, PostAdmin) # Чтобы не выносить отдельно регистрацию модели, можно использовать декоратор- это предпочтительный способ. Особенно, когда моделей много. https://docs.djangoproject.com/en/4.0/ref/contrib/admin/#django.contrib.admin.register


class GroupAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "slug", "description",)
    search_fields = ("title",)
    empty_value_display = "-пусто-"


admin.site.register(Group, GroupAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'post', 'author', 'text', 'created',)
    search_fields = ('text',)
    list_filter = ('author',)
    search_fields = ('author', 'created') # дубль на 28 строке


admin.site.register(Comment, CommentAdmin)


class FollowAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author')
    list_filter = ('author',)
    search_fields = ('author', 'user')


admin.site.register(Follow, FollowAdmin)
