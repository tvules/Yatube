import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from ..models import Post, Group

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    """Тестирование формы PostForm."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='TestTitle',
            slug='test_slug',
            description='TestDescription',
        )
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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(user=self.user)

    def test_create_new_post_form(self):
        """Тестирование формы создания нового поста."""
        form_data = {
            'text': 'NewPostTest',
            'group': self.group.id,
            'image': self.uploaded_image
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': self.user.get_username()}
            ),
        )
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group'],
                image=f"posts/{form_data['image'].name}"
            ).exists()
        )

    def test_edit_post_form(self):
        """Тестирование формы редактирования поста."""
        post = Post.objects.create(
            text='TestText',
            author=self.user,
            group=self.group,
        )
        form_data = {
            'text': 'EditPostTest',
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit', kwargs={'post_id': post.id}
            ),
            form_data,
            follow=True,
        )
        post.refresh_from_db()
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group, form_data.get('group'))
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail', kwargs={'post_id': post.id}
            )
        )
        self.assertTrue(
            Post.objects.filter(
                id=post.id,
                text=form_data['text'],
            ).exists()
        )


class CommentFormTest(TestCase):
    """Тестирование формы CommentForm."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.post = Post.objects.create(
            text='TestText',
            author=cls.user,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(user=self.user)

    def test_add_comment_form(self):
        """Тестирование работоспособности формы. Комментарий сохраняется."""
        form = {
            'text': 'TestComment',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form,
        )
        self.assertTrue(
            self.post.comments.filter(text=form['text']).exists()
        )
