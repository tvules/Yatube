import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Post, Group, Follow

EXPECTED_POST_FORM_FIELDS = {
    'text': forms.CharField,
    'group': forms.ModelChoiceField,
    'image': forms.ImageField
}

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):
    """Тест view приложения posts."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.raw_image = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded_image = SimpleUploadedFile(
            name='TestImage.gif',
            content=cls.raw_image,
            content_type='image/gif',
        )
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='TestTitle',
            slug='test_slug',
            description='TestDescription',
        )
        cls.other_group = Group.objects.create(
            title='TestTitleOther',
            slug='test_slug_other',
            description='TestDescriptionOther',
        )
        cls.post = Post.objects.create(
            text='TestText',
            author=cls.user,
            group=cls.group,
            image=cls.uploaded_image,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(user=self.user)
        cache.clear()

    def test_pages_uses_correct_template(self):
        """Проверка используемого шаблона для URL-адреса."""
        pages_templates_names = {
            reverse(
                'posts:index'
            ): 'posts/index.html',
            reverse(
                'posts:post_create'
            ): 'posts/create_post.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.user.get_username()},
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id},
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id},
            ): 'posts/create_post.html',
        }
        for reverse_name, template in pages_templates_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Проверка контекста для view-index."""
        response = self.authorized_client.get(reverse('posts:index'))
        post_obj = response.context.get('page_obj')[0]
        self._post_fields_testing(post_obj)

    def test_group_posts_page_show_correct_context(self):
        """Проверка контекста для view-group_posts."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug},
            ),
        )
        self.assertEqual(
            response.context.get('group'),
            self.group,
        )
        post_obj = response.context.get('page_obj')[0]
        self._post_fields_testing(post_obj)

    def test_profile_page_show_correct_context(self):
        """Проверка контекста для view-profile."""
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user.get_username()},
            ),
        )
        self.assertEqual(
            response.context.get('author'),
            self.post.author,
        )
        post_obj = response.context.get('page_obj')[0]
        self._post_fields_testing(post_obj)

    def test_post_detail_page_show_correct_context(self):
        """Проверка контекста для view-post_detail."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id},
            ),
        )
        post_obj = response.context.get('post')
        self._post_fields_testing(post_obj)

    def test_post_create_page_show_correct_context(self):
        """Проверка контекста для view-post_create."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_obj = response.context.get('form')
        self._post_form_fields_testing(form_obj)

    def test_post_edit_page_show_correct_context(self):
        """Проверка контекста для view-post_edit."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id},
            ),
        )
        form_obj = response.context.get('form')
        self.assertEqual(form_obj.instance, self.post)
        self._post_form_fields_testing(form_obj)

    def test_new_post_on_correct_pages(self):
        """Пост появляется где должен."""
        pages_which_post = [
            reverse(
                'posts:index'
            ),
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': self.user.get_username()},
            ),
        ]
        for page in pages_which_post:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertIn(
                    self.post,
                    response.context.get('page_obj'),
                )

    def test_post_in_correct_group(self):
        """Пост в правильной группе."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.other_group.slug}
            ),
        )
        self.assertNotIn(
            self.post,
            response.context.get('page_obj'),
        )

    def _post_fields_testing(self, post_obj: Post):
        """Сравнивает значения полей с ожидаемыми."""
        expected_field_value = {
            'text': self.post.text,
            'pub_date': self.post.pub_date,
            'author': self.post.author,
            'group': self.post.group,
            'image': self.post.image,
        }
        for field, expected_value in expected_field_value.items():
            self.assertEqual(getattr(post_obj, field), expected_value)

    def _post_form_fields_testing(self, form_obj: PostForm):
        """Сравнивает поля формы с ожидаемыми."""
        post_obj = form_obj.instance
        if post_obj.id is not None:
            self._post_fields_testing(post_obj)
        for field, expected_type in EXPECTED_POST_FORM_FIELDS.items():
            form_field = form_obj.fields.get(field)
            self.assertIsInstance(form_field, expected_type)


class PaginatorViewsTest(TestCase):
    """Тест пагинатора."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='TestTitle',
            slug='test_slug',
            description='TestDescription',
        )
        posts_obj = [
            Post(text='TestText', author=cls.user, group=cls.group)
            for _ in range(settings.POSTS_PER_PAGE * 2)
        ]
        cls.posts = Post.objects.bulk_create(posts_obj)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(user=self.user)
        cache.clear()

    def test_page_pagination(self):
        """Проверяет пагинацию страницы."""
        urls = {
            'index': reverse(
                'posts:index'
            ),
            'group_posts': reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ),
            'profile': reverse(
                'posts:profile',
                kwargs={'username': self.user.get_username()},
            ),
        }
        for view, url in urls.items():
            with self.subTest(view=view):
                self._pagination_testing(url)

    def _pagination_testing(self, url):
        first_page_response = self.authorized_client.get(url)
        second_page_response = self.authorized_client.get(url + '?page=2')
        self.assertEqual(
            len(first_page_response.context.get('page_obj')),
            settings.POSTS_PER_PAGE,
        )
        self.assertEqual(
            len(second_page_response.context.get('page_obj')),
            settings.POSTS_PER_PAGE,
        )


class CacheViewsTests(TestCase):
    """Тест кеширования."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.post = Post.objects.create(
            text='TestText',
            author=cls.user,
        )
        cls.URLS = {
            'index_page': reverse('posts:index')
        }

    def setUp(self):
        cache.clear()

    def test_cache_index_page(self):
        url = self.URLS['index_page']
        response = self._get_response(url)
        self.post.delete()
        self.assertEqual(
            self._get_response(url).content,
            response.content,
        )
        cache.clear()
        self.assertNotEqual(
            self._get_response(url).content,
            response.content,
        )

    def _get_response(self, url):
        return self.client.get(url)


class FollowViewsTests(TestCase):
    """Тест подписки на авторов."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='TestUserAuthor')
        cls.user_follower = User.objects.create_user(username='TestUser')
        cls.user_auth = User.objects.create_user('TestAuthUser')
        cls.post = Post.objects.create(
            text='TestText',
            author=cls.user_author,
        )

    def setUp(self):
        self.client.force_login(self.user_auth)
        self.client_author = Client()
        self.client_author.force_login(self.user_author)
        self.client_follower = Client()
        self.client_follower.force_login(self.user_follower)

    def test_following(self):
        """Юзер может подписаться на автора."""
        self.client_follower.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.user_author.get_username()}
            ),
        )
        self.assertTrue(
            Follow.objects.filter(
                user=self.user_follower,
                author=self.user_author,
            ).exists()
        )

    def test_unfollowing(self):
        """Юзер может отменить подписку на автора."""
        self.client_follower.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.user_author.get_username()}
            ),
        )
        self.assertFalse(
            Follow.objects.filter(
                user=self.user_follower,
                author=self.user_author,
            ).exists()
        )

    def test_post_in_follow_page(self):
        """Пост появляется на странице /posts/follow/"""
        self.client_follower.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.user_author.get_username()}
            ),
        )
        response = self.client_follower.get(reverse('posts:follow_index'))
        self.assertIn(self.post, response.context.get('page_obj'))

    def test_post_not_in_follow_page(self):
        """Пост не появляется на странице /posts/follow/"""
        response = self.client.get(reverse('posts:follow_index'))
        self.assertNotIn(self.post, response.context.get('page_obj'))