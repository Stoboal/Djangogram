from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
import uuid


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    image = models.ImageField(upload_to='users_image', null=True, blank=True)
    biography = models.TextField(max_length=512, null=True, blank=True)
    nickname = models.CharField(max_length=64, null=True, blank=True)

    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name='default_user',
        related_query_name='user'
    )

    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="default_user_permissions",
        related_query_name="user",
    )


class Tag(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tag'


class Comment(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    post = models.ForeignKey('Post', related_name='comments', on_delete=models.CASCADE)
    text = models.TextField(max_length=512)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username} - {self.text}'

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comment'


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='posts_images')
    description = models.TextField(max_length=1024, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(Tag, related_name='users', blank=True)

    def __str__(self):
        return f'{self.user.username} - {self.id}'

    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Post'


class LikePost(models.Model):
    post = models.ForeignKey('Post', related_name='likes', on_delete=models.CASCADE)
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'LikePost'
        verbose_name_plural = 'LikePost'


class LikeComment(models.Model):
    comment = models.ForeignKey('Comment', related_name='likes', on_delete=models.CASCADE)
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'LikeComment'
        verbose_name_plural = 'LikeComment'


class Subscription(models.Model):
    follower = models.ForeignKey('User', related_name='following', on_delete=models.CASCADE)
    followed = models.ForeignKey('User', related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'followed')

    @classmethod
    def follow(cls, user: User):
        if not cls.is_following(user):
            Subscription.objects.create(follower=self, followed=user)

    def unfollow(self, user: User):
        if self.is_following(user):
            Subscription.objects.filter(follower=self, followed=user).delete()

    def is_following(self, user: User):
        return Subscription.objects.filter(follower=self, followed=user).exists()

    def followers(self):
        return User.objects.filter(following__followed=self)

    def following(self):
        return User.objects.filter(followers__follower=self)
