from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic.base import RedirectView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.views.generic.list import ListView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page


from .forms import PostForm, CommentForm
from .models import Post, Group, Comment, User, Follow
from .utils import AuthorRequiredMixin


@method_decorator(cache_page(20, key_prefix='index_page'), name='dispatch')
class IndexListView(ListView):
    """Главная страница, на которой отображаются все посты пользователей."""
    model = Post
    paginate_by = settings.POSTS_PER_PAGE
    template_name = 'posts/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['index'] = True
        return context


class GroupListView(ListView):
    """Страница с постами определенной группы."""
    paginate_by = settings.POSTS_PER_PAGE
    template_name = 'posts/group_list.html'

    def get_queryset(self):
        self.group = get_object_or_404(Group, slug=self.kwargs['slug'])
        return self.group.posts.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = self.group
        return context


class ProfileListView(ListView):
    """Страница-profile определенного юзера."""
    paginate_by = settings.POSTS_PER_PAGE
    template_name = 'posts/profile.html'

    def get_queryset(self):
        self.author = get_object_or_404(User, username=self.kwargs['username'])
        return self.author.posts.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author'] = self.author
        context['following'] = self.is_follow()
        return context

    def is_follow(self) -> bool:
        if not self.request.user.is_authenticated:
            return False
        return Follow.objects.filter(
            user=self.request.user,
            author=self.author,
        ).exists()


class PostDetailView(DetailView):
    """Подробная страница определенного поста."""
    model = Post
    template_name = 'posts/post_detail.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.all()
        context['form'] = CommentForm()
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    """Страница создания нового поста."""
    template_name = 'posts/create_post.html'
    form_class = PostForm

    def get_success_url(self):
        return reverse(
            'posts:profile',
            kwargs={'username': self.object.author.get_username()},
        )

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = False
        return context


class PostEditView(LoginRequiredMixin, AuthorRequiredMixin, UpdateView):
    """Страница редактирования определенного поста."""
    model = Post
    template_name = 'posts/create_post.html'
    form_class = PostForm
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        return context


class AddCommentView(LoginRequiredMixin, CreateView):
    """Создание нового комментария к посту."""
    http_method_names = ['post']
    form_class = CommentForm

    def form_valid(self, form):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        form.instance.author = self.request.user
        form.instance.post = post
        return super().form_valid(form)


class FollowListView(LoginRequiredMixin, ListView):
    """Страница с постами авторов, на который подписан пользователь."""
    model = Post
    paginate_by = settings.POSTS_PER_PAGE
    template_name = 'posts/follow.html'

    def get_queryset(self):
        return Post.objects.filter(author__following__user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['follow'] = True
        return context


class ProfileFollowView(LoginRequiredMixin, RedirectView):
    """Создание подписки на определенного автора."""
    pattern_name = 'posts:profile'

    def get(self, request, *args, **kwargs):
        self.follow(request)
        return super().get(request, *args, **kwargs)

    def follow(self, request, *args, **kwargs):
        author = get_object_or_404(User, username=self.kwargs['username'])
        if author != request.user:
            Follow.objects.get_or_create(
                user=self.request.user,
                author=author,
            )


class ProfileUnFollowView(LoginRequiredMixin, RedirectView):
    """Отмена подписки на определенного автора."""
    pattern_name = 'posts:profile'

    def get(self, request, *args, **kwargs):
        self.unfollow(request)
        return super().get(request, *args, **kwargs)

    def unfollow(self, request):
        author = get_object_or_404(User, username=self.kwargs['username'])
        if author != self.request.user:
            Follow.objects.filter(
                user=self.request.user,
                author=author
            ).delete()