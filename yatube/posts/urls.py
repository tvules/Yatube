from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    path(
        '',
        views.IndexListView.as_view(),
        name='index'
    ),
    path(
        'create/',
        views.PostCreateView.as_view(),
        name='post_create'
    ),
    path(
        'profile/<str:username>/',
        views.ProfileListView.as_view(),
        name='profile'
    ),
    path(
        'group/<slug:slug>/',
        views.GroupListView.as_view(),
        name='group_list'
    ),
    path(
        'posts/<int:post_id>/',
        views.PostDetailView.as_view(),
        name='post_detail'
    ),
    path(
        'posts/<int:post_id>/edit/',
        views.PostEditView.as_view(),
        name='post_edit'
    ),
    path(
        'posts/<int:post_id>/comment/',
        views.AddCommentView.as_view(),
        name='add_comment'
    ),
    path(
        'follow/',
        views.FollowListView.as_view(),
        name='follow_index',
    ),
    path(
        'profile/<str:username>/follow/',
        views.ProfileFollowView.as_view(),
        name='profile_follow',
    ),
    path(
        'profile/<str:username>/unfollow/',
        views.ProfileUnFollowView.as_view(),
        name='profile_unfollow',
    ),
]