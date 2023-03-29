from django.test import TestCase, Client

# если это метод у тестированию, то он должен быть в ViewTestClass
def setUp(self) -> None:
    self.guest_client = Client()


class ViewTestClass(TestCase):
    def test_error_page(self):
        response = self.guest_client.get('/nonexist-page/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'core/404.html',)
