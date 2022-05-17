from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db import models

User = get_user_model()


class Group(models.Model):
    """Модель для сообществ."""
    title = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Название не должно превышать 200 символов.',
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='slug',
        help_text='Должен быть уникальным.',
    )
    description = models.TextField(
        verbose_name='Описание',
    )

    def __str__(self):
        return self.title


class Post(models.Model):
    """Модель для постов."""
    text = models.TextField(
        verbose_name='Текст',
        help_text='Текст нового поста'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Сообщество',
        help_text='Данный параметр необязательный'
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='posts/',
        blank=True,
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:15]

    def get_absolute_url(self):
        return reverse('posts:post_detail', kwargs={'post_id': self.pk})


class Comment(models.Model):
    """Модель для комментариев."""

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
    )
    text = models.TextField(
        verbose_name='Текст',
        help_text='Текст комментария',
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:15]

    def get_absolute_url(self):
        return reverse('posts:post_detail', kwargs={'post_id': self.post_id})


class Follow(models.Model):
    """Модель для подписок на авторов."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'