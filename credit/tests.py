
from django.urls import reverse
from django.test import TestCase
from .models import CustomUser, Profile, Post, Like
from .forms import SignupForm, ProfileForm
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import timedelta
from django.utils import timezone


class SignUpTest(TestCase):
    def test_valid_registration(self):
        response = self.client.post(reverse('signup'), {
            'username': 'testuser',
            'email': 'test@example.com',
            'email_conf': 'test@example.com',
            'password': 'testpassword',
            'password_conf': 'testpassword',
        })

        user = CustomUser.objects.get(username='testuser')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profile', kwargs={'user_id': user.id}))
        self.assertEqual(CustomUser.objects.count(), 1)

    def test_profile_object_create(self):
        user = get_user_model().objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        Profile.objects.create(user=user, username='testuser', content='これはデフォルトのプロフィールです。好みに応じて編集してください')
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(reverse('profile', kwargs={'user_id': user.id}))

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, 'testuser')
        self.assertContains(response, 'これはデフォルトのプロフィールです。好みに応じて編集してください')

    def test_invalid_registration_email(self):
        response = self.client.post(reverse('signup'), {
            'username': 'testuser',
            'email': 'test@example.com',
            'email_conf': 'tact@example.com',
            'password': 'testpassword',
            'password_conf': 'testpassword',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'メールアドレスが一致しません')
        self.assertEqual(CustomUser.objects.count(), 0)

    def test_invalid_registration_password(self):
        response = self.client.post(reverse('signup'), {
            'username': 'testuser',
            'email': 'test@example.com',
            'email_conf': 'test@example.com',
            'password': 'testpaccword',
            'password_conf': 'testpassword',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'パスワードが一致しません')
        self.assertEqual(CustomUser.objects.count(), 0)

class LoginTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser', email='test@example.com', password='testpassword')

    def test_login_success(self):
        logged_in = self.client.login(username='testuser', password='testpassword')
        print(logged_in)
        self.assertTrue(logged_in)

        response = self.client.get(reverse('top'))
        self.assertEqual(response.status_code, 200)

    def test_login_fail(self):
        logged_in = self.client.login(username='testuser', password='tactpassword')
        self.assertFalse(logged_in)

        response = self.client.post(reverse('login_view'))
        self.assertContains(response, 'ユーザーネームかパスワードが違います、もう一度お試しください')


class LogoutTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

    def test_logout(self):
        response = self.client.get(reverse('logout_view'))
        self.assertRedirects(response, reverse('top'))
        self.assertFalse(response.wsgi_request.user.is_authenticated)

class ProfileEditTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        self.profile = Profile.objects.create(user=self.user, username='testuser', content='test content')
        self.backimage = SimpleUploadedFile(name='刃牙.jpg', content=open('/code/media/item_images/Baki_Kengan-Collab_Horizontal_JA.jpg', 'rb').read(), content_type='image/jpg')
        self.image = SimpleUploadedFile(name='ハルメ.jpg', content=open('/code/media/item_images/ハルメ.jpg', 'rb').read(), content_type='image/jpg')

    def test_edit(self):
        response = self.client.post(reverse('profile_edit'), {
            'username': 'updateduser',
            'content': 'updated content',
            'image': self.image,
            'backimage': self.backimage
        })
        self.assertRedirects(response, reverse('profile', kwargs={'user_id': self.user.id}))

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.username, 'updateduser')
        self.assertEqual(self.profile.content, 'updated content')
        self.assertIsNotNone(self.profile.image)
        self.assertIsNotNone(self.profile.backimage)


class PostTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(username='testuser', password='12345')
        self.image = SimpleUploadedFile(name='フリー女.jpeg', content=open('/code/media/item_images/フリー女.jpeg', 'rb').read(), content_type='image/jpeg')

    def test_post(self):
        post = Post.objects.create(user=self.user, period='period', image=None, content='content')
        self.assertEqual(post.period, 'period')
        self.assertEqual(post.content, 'content')

    def test_image_post(self):
        post = Post.objects.create(user=self.user, period='period', image=self.image, content='content')
        self.assertIsNotNone(post.image)

    def test_post_descending_order(self):
        now = timezone.now()

        post1 = Post.objects.create(user=self.user, period='period2', image=None, content='content2', timestamp= now - timedelta(days=2))
        post2 = Post.objects.create(user=self.user, period='period1', image=None, content='content1', timestamp= now - timedelta(days=1))

        latest_posts = Post.objects.all().order_by('-timestamp')

        self.assertEqual(list(latest_posts), [post2, post1])


class LikeTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(username='testuser', password='12345')
        self.post = Post.objects.create(user=self.user, period='period', content='content')

    def test_like(self):
        Like.objects.create(user=self.user, post=self.post, is_liked=True)
        self.post.like_count += 1
        self.assertEqual(self.post.like_count, 1)

    def test_unlike(self):
        like = Like.objects.create(user=self.user, post=self.post, is_liked=True)
        self.post.like_count += 1
        like.delete()
        self.post.like_count -= 1 if self.post.like_count > 0 else 0
        self.assertEqual(self.post.like_count, 0)

    def test_multiple_likes(self):
        user2 = CustomUser.objects.create(username='testuser2', password='12345')
        Like.objects.create(user=self.user, post=self.post)
        self.post.like_count += 1
        Like.objects.create(user=user2, post=self.post)
        self.post.like_count += 1
        self.assertEqual(self.post.like_count, 2)

class FollowTests(TestCase):
    def setUp(self):
        self.user1 = CustomUser.objects.create(username='user1', password='password1')
        self.client.login(username='user1', password='password1')
        self.user2 = CustomUser.objects.create(username='user2', password='password2')

    def test_follow_user(self):
        self.user1.profile.follows.add(self.user2.profile)
        self.assertTrue(self.user1.profile.follows.filter(id=self.user2.profile.id).exists())

    def test_unfollow_user(self):
        self.user1.profile.follows.add(self.user2.profile)
        self.user1.profile.follows.remove(self.user2.profile)
        self.assertFalse(self.user1.profile.follows.filter(id=self.user2.profile.id).exists())
