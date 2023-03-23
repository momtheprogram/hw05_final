from django.test import TestCase

from ..models import Post


class PostModelTest(TestCase):

    def test_post_str(self):
        post = Post(text="Короткий пост")
        self.assertEqual(str(post), "Короткий пост")

        long_post = Post(text="Видим первые 15 символов")
        self.assertEqual(str(long_post), "Видим первые 15")
