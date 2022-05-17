from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post, Group

User = get_user_model()


class StaticURLTests(TestCase):

    def setUp(self) -> None:
        self.guest_client = Client()

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)


class PostsURLTests(TestCase):
    """Тесты URLs."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.user_author = User.objects.create_user(username='PostAuthor')
        cls.group = Group.objects.create(
            title='TestTitle',
            slug='test_slug',
            description='TestDescription',
        )
        cls.post = Post.objects.create(
            text='TestText',
            author=cls.user_author,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(self.user_author)
        self.URLS = {
            f'/group/{self.group.slug}/': {
                'access': 'free',
                'url_path': '/group/<slug>/',
                'template': 'posts/group_list.html',
            },
            f'/profile/{self.user_author.get_username()}/': {
                'access': 'free',
                'url_path': '/profile/<username>/',
                'template': 'posts/profile.html',
            },
            f'/posts/{self.post.id}/': {
                'access': 'free',
                'url_path': '/posts/<post_id>/',
                'template': 'posts/post_detail.html',
            },
            f'/posts/{self.post.id}/edit/': {
                'access': 'author',
                'url_path': '/posts/<post_id>/edit/',
                'template': 'posts/create_post.html',
            },
            f'/posts/{self.post.id}/comment/': {
                'access': 'auth',
                'url_path': '/posts/<post_id>/comment/',
                'template': None,
            },
            '/create/': {
                'access': 'auth',
                'template': 'posts/create_post.html',
            },
            f'/profile/{self.user_author.get_username()}/follow/': {
                'access': 'auth',
                'url_path': '/profile/<username>/follow/',
                'template': None,
            },
            f'/profile/{self.user_author.get_username()}/unfollow/': {
                'access': 'free',
                'url_path': '/profile/<username>/unfollow/',
                'template': None,
            },
        }

    def test_non_existent_url(self):
        """Проверка несуществующего url."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_exists_at_desired_location(self):
        """Проверка доступности ожидаемых urls."""
        for url, details in self.URLS.items():
            with self.subTest(url=url):
                response = self.author_client.get(url, follow=True)
                self.assertIn(
                    response.status_code,
                    (HTTPStatus.OK, HTTPStatus.METHOD_NOT_ALLOWED),
                    (f'Страница `{details.get("url_path", url)}` не найдена, '
                     f'проверьте этот адрес в *urls.py*')
                )

    def test_urls_uses_correct_template(self):
        """Проверка используемого шаблона для URL-адреса."""
        for url, details in self.URLS.items():
            if details['template'] is not None:
                with self.subTest(url=url):
                    response = self.author_client.get(url)
                    self.assertTemplateUsed(
                        response,
                        details['template'],
                        (f'URL-адрес `{details.get("url_path", url)}` '
                         f'использует не соответствующий html-шаблон.')
                    )

    def test_urls_redirect_anonymous_on_login(self):
        """Проверка редиректа для неавторизованных пользователей."""
        for url, details in self.URLS.items():
            with self.subTest(url=url):
                if details['access'] != 'free':
                    response = self.guest_client.get(url, follow=True)
                    self.assertRedirects(
                        response,
                        reverse(settings.LOGIN_URL) + f'?next={url}',
                    )
