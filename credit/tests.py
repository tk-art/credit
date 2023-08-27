
from django.urls import reverse
from django.test import TestCase
from .models import CustomUser, Profile
from .forms import SignupForm, ProfileForm
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

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

    def test_edit(self):
        response = self.client.post(reverse('profile_edit'), {
            'username': 'updateduser',
            'content': 'updated content',
        })
        self.assertRedirects(response, reverse('profile', kwargs={'user_id': self.user.id}))

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.username, 'updateduser')
        self.assertEqual(self.profile.content, 'updated content')