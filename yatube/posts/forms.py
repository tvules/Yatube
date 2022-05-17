from django.forms import ModelForm

from .models import Post, Comment


class PostForm(ModelForm):
    """Форма для создания/редактирования нового поста."""

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')


class CommentForm(ModelForm):
    """Форма для создания/редактирования комментария."""

    class Meta:
        model = Comment
        fields = ('text',)
