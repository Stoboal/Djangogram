from django.urls import path
from .views import *

urlpatterns = [
    path('', IndexPageView.as_view(), name='index'),

    path('users/<str:username>', UserPageView.as_view(), name='user_page'),
    path('users/<str:username>/update', UserProfileUpdateView.as_view(), name='settings'),
    path('register', register_view, name='register'),
    path('login', login_view, name='login'),
    path('logout', logout_view, name='logout'),


    path('posts/<uuid:post_id>/', PostDetailView.as_view(), name='post_page'),
    path('posts/create', create_post_view, name='create_post'),
    path('posts/<uuid:post_id>/like', like_post_view, name='like_post'),
    path('posts/<uuid:post_id>/delete', delete_post_view, name='delete_post'),
    path('posts/<uuid:post_id>/edit', update_post_description_view, name='edit_description'),
    path('posts/<uuid:post_id>/tags/create', create_tag_for_post_view, name='create_tags'),
    path('posts/<uuid:post_id>/tags/<int:tag_id>/remove', remove_tag_from_post_view, name='remove_tag'),

    path('comments/<uuid:post_id>/create', create_comment_view, name='create_comment'),
    path('comments/<int:comment_id>/update', update_comment_view, name='update_comment'),
    path('comments/<int:comment_id>/like', like_comment_view, name='like_comment'),
    path('comments/<int:comment_id>/delete', delete_comment_view, name='delete_comment'),

    path('tags/<str:name>', TagPageView.as_view(), name='tag_page'),

    path('reactions/<str:username>', ReactPageView.as_view(), name='reactions_page'),
    path('users/follow/<str:user_id>', follow_view, name='follow_user')
]
