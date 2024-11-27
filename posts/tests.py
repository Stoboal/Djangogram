from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.models import User, Post, Tag, LikePost, Comment, Subscription

import io
from PIL import Image


class DjangogramTestCase(TestCase):
    @staticmethod
    def _create_test_image(self):
        img = Image.new('RGB', (100, 100), color=(73, 109, 137))
        img_io = io.BytesIO()
        img.save(img_io, format='JPEG')
        img_io.seek(0)
        test_image = SimpleUploadedFile('test_image.jpg', img_io.read(), content_type='image/jpeg')
        return test_image

    def setUp(self):
        # Test User
        self.username = 'username'
        self.password = 'psswrd3c2x1z@@'
        self.user = User.objects.create(username=self.username, email='username333@gmal.ca')
        self.user.set_password(self.password)
        self.user.save()

        # Test Post
        self.image = self._create_test_image(self)
        self.post = Post.objects.create(
            description='Test description',
            user=self.user,
            image=self.image
        )
        self.post.tags.add(Tag.objects.create(name='123'))
        self.post.save()

    def test_login_view_valid_data(self):
        response = self.client.post(reverse('login'), {'username': self.username, 'password': self.password})

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('index'))
        self.assertTrue(self.client.login(username=self.username, password=self.password))

    def test_login_view_invalid_data(self):
        response = self.client.post(reverse('login'), {'username': self.username, 'password': 'abrakadabra'})

        self.assertIn('form', response.context)
        self.assertTrue(response.context['form'].errors)

    def test_register_view_valid_data(self):
        response = self.client.post(reverse('register'), {
            'username': 'IvanIvan',
            'email': 'ivan@gmal.ca',
            'password1': self.password,
            'password2': self.password
        })

        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.get(email='ivan@gmal.ca').username == 'IvanIvan')

    def test_register_view_invalid_data(self):
        response = self.client.post(reverse('register'), {
            'username': 'IvanIvan',
            'email': 'ivangmal.ca',
            'password1': self.password,
            'password2': self.password
        })
        form = response.context['form']

        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors)

    def test_logout_view(self):
        self.client.post(reverse('login'), {'username': self.username, 'password': self.password})
        response = self.client.get(reverse('logout'))

        self.assertEqual(response.status_code, 302)
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_create_post_valid_data(self):
        url = reverse('create_post')
        image = self._create_test_image(self)
        tags = 'tag1, tag2'
        data = {
            'description': 'Test valid',
            'image': image,
            'tags': tags
        }
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(url, data, follow=True)

        self.assertRedirects(response, reverse('index'))

        post = Post.objects.get(description='Test valid')

        self.assertEqual(post.user, self.user)
        self.assertEqual(post.tags.count(), 2)
        self.assertTrue(post.image)

    def test_create_post_invalid_data(self):
        url = reverse('create_post')
        tags = 'tag1, tag2'
        data = {
            'description': 'Test invalid',
            'tags': tags
        }
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(url, data)
        form = response.context['form']

        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors)

    def test_delete_post(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(reverse('delete_post', args=[self.post.id]), follow=True)

        self.assertRedirects(response, reverse('index'))
        with self.assertRaises(Post.DoesNotExist):
            Post.objects.get(id=self.post.id)

    def test_like_and_dislike_post(self):
        self.client.login(username=self.username, password=self.password)

        # Like
        response = self.client.post(reverse('like_post', kwargs={'post_id': self.post.id}), follow=True)
        self.assertJSONEqual(response.content, {'success': True, 'liked': True, 'likes_count': 1})
        self.assertTrue(LikePost.objects.filter(post=self.post, user=self.user).exists())

        # Dislike
        response = self.client.post(reverse('like_post', kwargs={'post_id': self.post.id}), follow=True)
        self.assertJSONEqual(response.content, {'success': True, 'liked': False, 'likes_count': 0})
        self.assertFalse(LikePost.objects.filter(post=self.post, user=self.user).exists())

    def test_update_description(self):
        self.client.login(username=self.username, password=self.password)
        new_description = 'New description'
        response = self.client.post(
            reverse('edit_description', kwargs={'post_id': self.post.id}),
            {'description': new_description},
            follow=True
        )
        self.assertRedirects(response, reverse('post_page', kwargs={'post_id': self.post.id}))
        self.post.refresh_from_db()
        self.assertEqual(self.post.description, new_description)

    def test_comment_actions(self):
        self.client.login(username=self.username, password=self.password)

        # Create
        comment_text = 'Comment text'
        create_comment_response = self.client.post(
            reverse('create_comment', kwargs={'post_id': self.post.id}),
            {'text': comment_text},
            follow=True
        )
        self.assertRedirects(create_comment_response, reverse('post_page', kwargs={'post_id': self.post.id}))
        self.assertTrue(Comment.objects.filter(text=comment_text, user=self.user, post=self.post).exists())

        comment = Comment.objects.get(text=comment_text, user=self.user, post=self.post)

        # Update
        updated_comment_text = 'Updated comment text'
        update_comment_response = self.client.post(
            reverse('update_comment', kwargs={'comment_id': comment.id}),
            {'text': updated_comment_text},
            follow=True
        )
        self.assertRedirects(update_comment_response, reverse('post_page', kwargs={'post_id': self.post.id}))
        comment.refresh_from_db()
        self.assertEqual(comment.text, updated_comment_text)

        # Delete
        delete_comment_response = self.client.post(
            reverse('delete_comment', kwargs={'comment_id': comment.id}),
            follow=True
        )
        self.assertRedirects(delete_comment_response, reverse('post_page', kwargs={'post_id': self.post.id}))
        self.assertFalse(Comment.objects.filter(id=comment.id).exists())

    def test_follow_functionality(self):
        self.client.login(username=self.username, password=self.password)
        user_2 = User.objects.create(username='TestUser2', email='<EMAIL>', password='<PASSWORD>')

        # Follow
        response = self.client.get(reverse('follow_user', args=[user_2.id]))
        self.assertJSONEqual(response.content, {'success': True, 'is_following': True})
        self.assertTrue(Subscription.objects.filter(follower=self.user, followed=user_2.id).exists())

        # Unfollow
        response = self.client.get(reverse('follow_user', args=[user_2.id]))
        self.assertJSONEqual(response.content, {'success': True, 'is_following': False})
        self.assertFalse(Subscription.objects.filter(follower=self.user, followed=user_2.id).exists())



