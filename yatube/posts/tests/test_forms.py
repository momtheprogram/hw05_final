import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.models import Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class FormTest(TestCase):
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
            content=FormTest.small_gif,
            content_type='image/gif'
        )
        cls.author = User.objects.create_user('author')
        cls.post = Post.objects.create(
            text='Текст',
            author=FormTest.author,
            image=FormTest.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(FormTest.author)

    def test_create_post(self):
        self.assertEqual(Post.objects.count(), 1)
        self.assertTrue(Post.objects.filter(text='Текст',
                                            image='posts/small.gif',
                                            author=self.author).exists())

    def test_change_post(self):
        post = Post.objects.create(
            text='Текст поста для его изменения',
            author=FormTest.author
        )
        form_data = {
            'text': 'Текст поста после его изменения',
        }
        self.authorized_client.post(reverse('posts:post_edit', args=[post.pk]),
                                    data=form_data, follow=True)
        post_after_changes = Post.objects.get(pk=post.pk)
        self.assertEqual(
            post_after_changes.text,
            form_data['text'],
            'Текст поста не изменился'
        )
        self.assertEqual(
            post_after_changes.pk,
            post.pk,
            'Вместо изменения поста, создается новый пост'
        )
