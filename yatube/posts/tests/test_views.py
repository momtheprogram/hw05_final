import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.conf import settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from ..forms import PostForm
from posts.models import Post, Group, Comment, Follow

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=PostPagesTests.small_gif,
            content_type='image/gif'
        )
        cls.author = User.objects.create_user('author')
        cls.group = Group.objects.create(
            title='Title',
            slug='slug',
            description='description'
        )
        cls.post = Post.objects.create(
            text='Текст',
            author=PostPagesTests.author,
            group=PostPagesTests.group,
            image=PostPagesTests.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        self.guest_client = Client()

        self.authorized_client = Client()
        self.authorized_client.force_login(PostPagesTests.author)

    def test_pages_uses_correct_template(self):
        args = {
            'kwargs': {'slug': self.group.slug},
            'author': {self.author},
            'id': {self.post.pk},
        }
        urls = {
            'group': 'posts/group_list.html',
            'profile': 'posts/profile.html',
            'detail': 'posts/post_detail.html',
            'create': 'posts/create_post.html',
        }
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs=args['kwargs']): urls['group'],
            reverse('posts:profile', args={self.author}): urls['profile'],
            reverse('posts:post_detail', args=args['id']): urls['detail'],
            reverse('posts:post_edit', args=args['id']): urls['create'],
            reverse('posts:post_create'): urls['create'],
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template,)

    def test_chek_context_index(self):
        response = self.authorized_client.get(reverse('posts:index'))
        first_obj = response.context['page_obj'][0].text
        image = response.context['page_obj'][0].image
        self.assertEqual(first_obj, self.post.text)
        self.assertEqual(image, 'posts/small.gif')

    def test_chek_context_group_list(self):
        response = (self.authorized_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': self.group.slug})
        ))
        obj_post = response.context['page_obj'][0].group
        obj_group = response.context['group']
        obj_image = response.context['page_obj'][0].image
        self.assertEqual(
            obj_post.title,
            self.group.title,
            (f'Пост отсутствует на страничке "posts/group_list.html"'
             f' в группе {obj_group}'),
        )
        self.assertEqual(obj_image, 'posts/small.gif')

    def test_chek_context_profile(self):
        another_post = Post.objects.create(
            text='Текст другого автора',
            author=self.author,
            image=self.uploaded
        )
        url = reverse('posts:profile', args=(another_post.author.username,))

        response = self.authorized_client.get(url)

        context_post = response.context['page_obj'][0]
        context_count = response.context['all_posts']
        context_author = response.context['author']
        self.assertEqual(context_post,
                         another_post,
                         'Некорректный контекст view "profile".'
                         )
        self.assertEqual(
            context_count,
            2,
            'В контексте profile некорректное число постов автора'
        )
        self.assertEqual(context_author, self.author)
        self.assertEqual(context_post.image, another_post.image)

    def test_chek_context_post_detail(self):
        response = self.authorized_client.get(reverse(
            'posts:post_detail',
            args=[self.post.pk]
        ))
        context_post = response.context['post']
        context_count = response.context['post_count']
        self.assertEqual(
            context_post,
            self.post,
            'Неверный пост в контекте post_detail'
        )
        self.assertEqual(
            context_count,
            self.author.posts.count(),
            'Неверное количеств постов в контексте post_detail'
        )
        self.assertEqual(context_post.image, 'posts/small.gif')

    def test_chek_context_create_post_edit(self):
        post_form = PostForm(instance=self.post)
        url = reverse('posts:post_edit', args=[self.post.pk])
        response = self.authorized_client.get(url)

        context_form = response.context['form']
        context_is_edit = response.context['is_edit']
        context_post = response.context['post']

        self.assertIsInstance(context_form, type(post_form),)
        self.assertEqual(context_is_edit, True,)
        self.assertEqual(context_post, self.post,)
        self.assertEqual(context_form.instance, self.post,)

    def test_chek_context_create_post(self):
        form_type = type(PostForm())
        response = self.authorized_client.get(reverse('posts:post_create'))
        context_form = response.context['form']
        context_is_edit = response.context['is_edit']
        self.assertIsInstance(context_form, form_type,)
        self.assertEqual(context_is_edit, False,)

    def test_check_post_in_pages_group(self):
        """
        Появление поста на главной странице, странице выбранной группы,
        в профайле пользователя, если при создании поста указать группу.
        """
        url_2 = reverse('posts:group_list', kwargs={'slug': self.group.slug})
        url_3 = reverse('posts:profile', args=(self.author.username,))
        response1 = self.authorized_client.get(reverse('posts:index'))
        response2 = self.authorized_client.get(url_2)
        response3 = self.authorized_client.get(url_3)

        context1 = response1.context['page_obj'][0]
        context2 = response2.context['page_obj'][0].group.title
        context3 = response3.context['page_obj'][0]

        self.assertEqual(
            context1,
            self.post,
            'На главной странице нет созданного с группой поста'
        )
        self.assertEqual(
            context2,
            self.post.group.title,
            f'В группе {self.group.title} нет созданного поста'
        )
        self.assertEqual(
            context3,
            self.post,
            (f'В профайле пользователя {self.author.username}'
             f' нет созданного поста')
        )

    def test_post_not_in_an_outsider_group(self):
        """
        Отсутствие поста в группе, для которой он не был предназначен.
        """
        group = Group.objects.create(
            title='Simple_title',
            slug='simple-slug',
            description='simple_description'
        )
        url = reverse('posts:group_list', kwargs={'slug': self.group.slug})
        response = self.authorized_client.get(url)
        group_context = response.context['page_obj'][0].group.title
        self.assertNotEqual(
            group_context,
            group.title,
            (f'Созданный пост попал в неверную группу {group.title}'
             f'вместо {self.post.group.title}')
        )


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='user-p')
        cls.group = Group.objects.create(
            title='title-p',
            slug='slug-p',
            description='description-p'
        )
        text = 'Тестовый текст для 13-ти постов для проверки паджинатора'
        for i in range(13):
            Post.objects.create(
                text=text,
                author=PaginatorViewsTest.author,
                group=PaginatorViewsTest.group,
            )

    def setUp(self) -> None:
        self.author_client = Client()
        self.author_client.force_login(PaginatorViewsTest.author)

    def test_paginate_1(self):
        """
        Работа паджинатора (количество постов
        на первой страничке, проверяем главную, отфильрованную по группам
        и профайл).
        """
        url_gr = reverse('posts:group_list', kwargs={'slug': self.group.slug})
        url_pr = reverse('posts:profile', args=[self.author.username],)
        response = self.author_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)
        response = self.author_client.get(url_gr)
        self.assertEqual(len(response.context['page_obj']), 10)
        response = self.author_client.get(url_pr)
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_paginate_2(self):
        """
        Работы паджинатора (количество постов на второй страничке).
        """
        response = self.author_client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)


class CommentTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user('user')
        cls.post = Post.objects.create(
            author=CommentTest.user,
            text='Пост',
        )

    def setUp(self) -> None:
        self.client_authorized = Client()
        self.client_guest = Client()
        self.client_authorized.force_login(CommentTest.user)
        self.comment = Comment.objects.create(
            text='Коммент',
            author_id=self.user.pk,
            post_id=self.post.pk,
        )

    def test_add_comment(self):
        """ Комментировать посты может только авторизованный пользователь. """

        comment = Comment.objects.filter(
            post=self.post,
            author=self.user,
            text=self.comment.text
        ).count()
        self.assertEqual(comment, 1)

        form_data = {'comment': 'Коммент гостя', }
        url = reverse('posts:add_comment', args=[self.post.pk],)
        self.client_guest.post(url, follow=True, data=form_data,)
        comment_guest = Comment.objects.filter(post_id=self.post.pk).count()
        self.assertEqual(comment_guest, 1)

        response = self.client_authorized.get(reverse(
            'posts:post_detail',
            args=[self.post.pk]
        ))
        self.assertEqual(response.context['comments'][0], self.comment)


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user('author')

    def setUp(self):
        self.user = User.objects.create_user(username='user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(FollowTest.author)

    def test_follow_unfollow(self):
        """
        Авторизованный пользователь может подписаться и отписаться от автора.
        """
        self.authorized_client.get(
            reverse('posts:profile_follow', args=[self.author.username])
        )
        self.assertEqual(Follow.objects.filter(user=self.user).count(), 1)

        self.authorized_client.get(
            reverse('posts:profile_unfollow', args=[self.author.username])
        )
        self.assertEqual(Follow.objects.all().count(), 0)

    def test_new_post_for_followers(self):
        """
        Новая запись появляется в ленте тех, кто подписан
        и не появляется в ленте тех, кто не подписан. """
        Follow.objects.create(user=self.user,
                              author=self.author)
        post = Post.objects.create(
            text="Авторский текст",
            author=self.author,)
        response = self.authorized_client.get('/follow/')
        post_for_followers = response.context["page_obj"][0].text
        self.assertEqual(post_for_followers, "Авторский текст")

        response = self.author_client.get('/follow/')
        post_none = response.context['page_obj']
        self.assertNotIn(post, post_none,)
