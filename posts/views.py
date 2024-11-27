from django.contrib import auth
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, UpdateView
from django.shortcuts import render, HttpResponseRedirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone

import os
from PIL import Image
from io import BytesIO

from .forms import *
from .models import Post, Tag, LikePost, Comment, LikeComment, Subscription


def login_view(request):
    if request.method == 'POST':
        form = UserAuthenticationForm(data=request.POST)
        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = auth.authenticate(request, username=username, password=password)
            if user:
                auth.login(request, user)
                return HttpResponseRedirect(reverse('index'), status=302)
            else:
                return render(request, 'posts/login.html', {'form': form})
    else:
        form = UserAuthenticationForm()
    return render(request, 'posts/login.html', {'form': form}, status=200)


def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('login'))
    else:
        form = UserRegisterForm()
    return render(request, 'posts/register.html', {'form': form}, status=401)


def logout_view(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('index'))


class IndexPageView(ListView):
    model = Post
    template_name = 'posts/index.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.all().order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_user_page'] = False
        return context


class UserPageView(ListView):
    model = Post
    template_name = 'posts/index.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        username = self.kwargs.get('username')
        self.user = get_object_or_404(User, username=username)
        return Post.objects.filter(user=self.user).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_user_page'] = True
        context['user'] = self.user
        context['is_following'] = Subscription.objects.filter(follower=self.request.user, followed=self.user).exists()
        return context


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'posts/settings.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('settings', kwargs={'username': self.request.user.username})

    def form_valid(self, form):
        form.instance.username = self.request.POST.get('username')
        form.instance.first_name = self.request.POST.get('first_name')
        form.instance.last_name = self.request.POST.get('last_name')
        form.instance.biography = self.request.POST.get('biography')
        form.instance.email = self.request.POST.get('email')

        if self.request.FILES.get('image'):
            image = self.request.FILES.get('image')
            new_filename = f"{self.request.user.id}_{self.request.user.username}_profileimage.jpg"

            # Open, resize and save/update user image
            img = Image.open(image)
            img = img.convert('RGB')
            img.thumbnail((800, 800), Image.Resampling.LANCZOS)
            img_io = BytesIO()
            img.save(img_io, format='JPEG', quality=85)
            img_content = ContentFile(img_io.getvalue(), new_filename)
            if self.request.user.image:
                if os.path.isfile(self.request.user.image.path):
                    os.remove(self.request.user.image.path)

            form.instance.image.save(new_filename, img_content)
        else:
            form.instance.image = self.request.user.image

        form.instance.save()
        return super().form_valid(form)


class TagPageView(ListView):
    model = Tag
    template_name = 'posts/index.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        name = self.kwargs.get('name')
        tag = get_object_or_404(Tag, name=name)
        return Post.objects.filter(tags__name=tag).order_by('-created_at')


class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/post.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        return super().get_object(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_id'] = self.object.id
        context['tags_form'] = AddPostTagsForm()
        context['comment_form'] = CommentForm()
        context['description_form'] = PostDescriptionForm()
        return context


class ReactPageView(ListView):
    template_name = 'posts/reactions.html'
    context_object_name = 'reactions'

    def get_queryset(self):
        user = self.request.user
        user_posts = Post.objects.filter(user=user).order_by('-created_at')
        user_comments = Comment.objects.filter(user=user).order_by('-created_at')
        subscribes = Subscription.objects.filter(followed=user).order_by('-created_at')
        all_reactions = []

        for post in user_posts:
            if post.comments.exists():
                all_reactions.extend(post.comments.all())
            if post.likes.exists():
                all_reactions.extend(post.likes.all())

        for comment in user_comments:
            if comment.likes.exists():
                all_reactions.extend(comment.likes.all())

        all_reactions += subscribes

        all_reactions = sorted(all_reactions, key=lambda x: x.created_at, reverse=True)
        return all_reactions


def create_post_view(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            description = form.cleaned_data['description']
            image = form.cleaned_data['image']
            tag_names = [tag.strip() for tag in form.cleaned_data['tags'].split(',')]
            tags = [Tag.objects.get_or_create(name=tag_name)[0] for tag_name in tag_names]

            # Generating unique image name
            user_id = request.user.id
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            filename, extension = os.path.splitext(image.name)
            new_filename = f'{user_id}_{timestamp}{extension}'

            # Changing image
            img = Image.open(image)
            img = img.convert('RGB')
            img.thumbnail((800, 800), Image.Resampling.LANCZOS)
            img_io = BytesIO()
            img.save(img_io, format='JPEG', quality=85)  # Save as JPEG with quality 85
            img_content = ContentFile(img_io.getvalue(), new_filename)

            # Saving Post
            post = Post.objects.create(description=description, user=request.user)
            post.image.save(new_filename, img_content)
            post.tags.set(tags)

            return HttpResponseRedirect(reverse_lazy('index'))
    else:
        form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})


def delete_post_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user

    if user.id == post.user.id:
        post.delete()
        return HttpResponseRedirect(reverse_lazy('index'))
    else:
        return HttpResponseRedirect(reverse('post_page', kwargs={'post_id': post_id}))


def like_post_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user

    if LikePost.objects.filter(post=post, user=user).exists():
        LikePost.objects.get(post=post, user=user).delete()
        liked = False
    else:
        like = LikePost(post=post, user=user)
        like.save()
        liked = True

    likes_count = LikePost.objects.filter(post=post).count()
    return JsonResponse({'success': True, 'liked': liked, 'likes_count': likes_count})


def create_tag_for_post_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = AddPostTagsForm(request.POST)
        if form.is_valid():
            tag_names = [tag.strip() for tag in form.cleaned_data['tags'].split(',')]
            tags = [Tag.objects.get_or_create(name=tag_name)[0] for tag_name in tag_names]
            for tag in tags:
                post.tags.add(tag)
    return HttpResponseRedirect(reverse('post_page', kwargs={'post_id': post_id}))


def remove_tag_from_post_view(request, post_id, tag_id):
    post = get_object_or_404(Post, id=post_id)
    tag = get_object_or_404(Tag, id=tag_id)
    post.tags.remove(tag)
    return HttpResponseRedirect(reverse('post_page', kwargs={'post_id': post_id}))


def update_post_description_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = PostDescriptionForm(request.POST)
        if form.is_valid():
            post.description = form.cleaned_data['description']
            post.save()
    return HttpResponseRedirect(reverse('post_page', kwargs={'post_id': post_id}))


def create_comment_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            comment = Comment.objects.create(text=text, user=request.user, post=post)
            comment.save()
            return HttpResponseRedirect(reverse('post_page', kwargs={'post_id': post_id}))
    else:
        form = CommentForm()
    return render(request, f'posts/{post_id}.html', {'form': form})


def update_comment_view(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    post_id = comment.post.id
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            comment.save()
            return HttpResponseRedirect(reverse('post_page', kwargs={'post_id': post_id}))
    else:
        form = CommentForm()
    return render(request, f'posts/{post_id}.html', {'form': form})


def like_comment_view(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    user = request.user
    post_id = comment.post.id

    if LikeComment.objects.filter(comment=comment, user=user).exists():
        LikeComment.objects.get(comment=comment, user=user).delete()
    else:
        like = LikeComment(comment=comment, user=user)
        like.save()

    return HttpResponseRedirect(reverse('post_page', kwargs={'post_id': post_id}))


def delete_comment_view(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    user = request.user
    post_id = comment.post.id

    if user.id == comment.user.id:
        comment.delete()

    return HttpResponseRedirect(reverse('post_page', kwargs={'post_id': post_id}))


def follow_view(request, user_id):
    follower = request.user
    followed = get_object_or_404(User, id=user_id)

    if follower != followed:
        if Subscription.objects.filter(follower=follower, followed=followed).exists():
            Subscription.objects.filter(follower=follower, followed=followed).delete()
            is_following = False
        else:
            Subscription.objects.create(follower=follower, followed=followed)
            is_following = True
    else:
        is_following = False

    return JsonResponse({'success': True, 'is_following': is_following})
