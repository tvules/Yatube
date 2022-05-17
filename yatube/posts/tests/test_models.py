from unittest import skipUnless

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Post, Group

User = get_user_model()


class PostModelTests(TestCase):
    """Тестирование модели Post."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='TestTitle',
            slug='test_slug',
            description='TestDescription',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test' * 10,
        )

    def test_models_have_correct_object_names(self):
        """Проверка корректности метода __str__."""
        post = self.post
        expected_object_name = post.text[:15]
        self.assertEqual(str(post), expected_object_name, (
            'Метод __str__ модели "Post" работает некорректно.'
        ))

    @skipUnless(settings.VERBOSE_NAME_TESTING,
                'Тестирование для verbose_name отключено в настройках')
    def test_verbose_name(self):
        """Проверка совпадения verbose_name поля с ожидаемым."""
        post = PostModelTests.post
        field_verboses = {
            'text': 'Текст',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Сообщество',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name,
                    expected_value,
                    (f'Значение "verbose_name" для поля "{field}" '
                     f'должно быть равно "{expected_value}".'),
                )

    @skipUnless(settings.HELP_TEXT_TESTING,
                'Тестирование для help_text отключено в настройках')
    def test_help_text(self):
        """Проверка совпадения help_text поля с ожидаемым."""
        post = PostModelTests.post
        field_help_texts = {
            'text': 'Текст нового поста',
            'group': 'Данный параметр необязательный',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text,
                    expected_value,
                    (f'Значение "help_text" для поля "{field}" '
                     f'должно быть равно "{expected_value}".')
                )

    def test_pub_date_auto_now_add(self):
        """Проверка совпадения auto_now_add поля pub_date с ожидаемым."""
        post = self.post
        field = 'pub_date'
        expected_value = True
        self.assertEqual(
            post._meta.get_field(field).auto_now_add,
            expected_value,
            (f'Значение "auto_now_add" для поля "{field}" '
             f'должно быть равно "{expected_value}".')
        )


class GroupModelTests(TestCase):
    """Тестирование модели Group."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='TestTitle',
            slug='test_slug',
            description='TestDescription',
        )

    def test_models_have_correct_object_names(self):
        """Проверка корректности метода __str__."""
        group = self.group
        expected_object_name = group.title
        self.assertEqual(str(group), expected_object_name, (
            'Метод __str__ модели "Group" работает некорректно.'
        ))

    @skipUnless(settings.VERBOSE_NAME_TESTING,
                'Тестирование для verbose_name отключено в настройках')
    def test_verbose_name(self):
        """Проверка совпадения verbose_name поля с ожидаемым."""
        group = self.group
        field_verboses = {
            'title': 'Название',
            'slug': 'slug',
            'description': 'Описание',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name,
                    expected_value,
                    (f'Значение "verbose_name" для поля "{field}" '
                     f'должно быть равно "{expected_value}".'),
                )

    @skipUnless(settings.HELP_TEXT_TESTING,
                'Тестирование для help_text отключено в настройках')
    def test_help_text(self):
        """Проверка совпадения help_text поля с ожидаемым."""
        group = self.group
        field_help_texts = {
            'title': 'Название не должно превышать 200 символов.',
            'slug': 'Должен быть уникальным.',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).help_text,
                    expected_value,
                    (f'Значение "help_text" для поля "{field}" '
                     f'должно быть равно "{expected_value}".')
                )

    def test_unique_slug(self):
        """Проверка совпадения unique поля slug c ожидаемым."""
        group = self.group
        field = 'slug'
        expected_value = True
        self.assertEqual(
            group._meta.get_field(field).unique,
            expected_value,
            (f'Значение "unique" для поля "{field}" '
             f'должно быть равно "{expected_value}".')
        )
