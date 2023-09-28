
from django.urls import reverse
from django.test import TestCase
from .models import CustomUser, Profile, Post, Like, Evidence, EvidenceImage, EvidenceRating, Notification
from .forms import SignupForm, ProfileForm, EvidenceForm, EvidenceImageForm
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

        self.profile = Profile.objects.create(user=self.user, username='user1', content='content')

    def test_login_success(self):
        logged_in = self.client.login(username='testuser', password='testpassword')
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
        post = Post.objects.create(user=self.user, image=None, content='content')
        self.assertIsNotNone(post.deadline)
        self.assertEqual(post.content, 'content')

    def test_image_post(self):
        post = Post.objects.create(user=self.user, image=self.image, content='content')
        self.assertIsNotNone(post.image)

    def test_post_descending_order(self):
        now = timezone.now()

        post1 = Post.objects.create(user=self.user, image=None, content='content2', timestamp= now - timedelta(days=2))
        post2 = Post.objects.create(user=self.user, image=None, content='content1', timestamp= now - timedelta(days=1))

        latest_posts = Post.objects.all().order_by('-timestamp')

        self.assertEqual(list(latest_posts), [post2, post1])


class LikeTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(username='testuser', password='12345')
        self.post = Post.objects.create(user=self.user, content='content')

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
        self.user2 = CustomUser.objects.create(username='user2', password='password2')

        self.profile1 = Profile.objects.create(user=self.user1, username='user1', content='content')
        self.profile2 = Profile.objects.create(user=self.user2, username='user2', content='content')

    def test_follow_user(self):
        self.user1.profile.follows.add(self.user2.profile)
        self.assertTrue(self.user1.profile.follows.filter(id=self.user2.profile.id).exists())

    def test_unfollow_user(self):
        self.user1.profile.follows.add(self.user2.profile)
        self.user1.profile.follows.remove(self.user2.profile)
        self.assertFalse(self.user1.profile.follows.filter(id=self.user2.profile.id).exists())

class EvidenceTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(username='testuser', password='12345')
        self.post = Post.objects.create(user=self.user, image=None, content='content')
        self.post2 = Post.objects.create(user=self.user, image=None, content='content')
        self.image = SimpleUploadedFile(name='フリー女.jpeg', content=open('/code/media/item_images/フリー女.jpeg', 'rb').read(), content_type='image/jpeg')

    def test_create_evidence(self):
        evidence = Evidence.objects.create(user=self.user, post=self.post, text='text')
        evidence_image = EvidenceImage.objects.create(evidence=evidence, image=self.image)
        self.assertEqual(evidence.text, 'text')
        self.assertIsNotNone(evidence_image.image)

    def test_valid_form(self):
        evidence = Evidence.objects.create(user=self.user, post=self.post, text='text')
        evidence_image = EvidenceImage.objects.create(evidence=evidence, image=self.image)
        form = EvidenceForm({'text':evidence.text})
        form_image = EvidenceImageForm({'image': evidence_image.image}, {'image':evidence_image.image})
        self.assertTrue(form.is_valid())
        self.assertTrue(form_image.is_valid())

    def test_evidence_descending_order(self):
        now = timezone.now()

        evidence1 = Evidence.objects.create(user=self.user, post=self.post, text='text', timestamp= now - timedelta(days=2))
        evidence2 = Evidence.objects.create(user=self.user, post=self.post2, text='text', timestamp= now - timedelta(days=1))


        latest_evidences = Evidence.objects.all().order_by('-timestamp')

        self.assertEqual(list(latest_evidences), [evidence2, evidence1])

class DeleteTest(TestCase):
    def setUp(self):
       self.user = CustomUser.objects.create_user(username='testuser', password='testpass')
       self.post = Post.objects.create(user=self.user, content='content')
       self.evidence = Evidence.objects.create(user=self.user, post=self.post, text='text')

    def test_delete_post(self):
        self.assertTrue(Post.objects.filter(content='content').exists())
        response = self.client.post(reverse('delete_post', args=[self.post.id]))
        self.assertFalse(Post.objects.filter(content='content').exists())

    def test_delete_evidence(self):
        self.assertTrue(Evidence.objects.filter(text='text').exists())
        response = self.client.post(reverse('delete_evidence', args=[self.evidence.id]))
        self.assertFalse(Evidence.objects.filter(text='text').exists())



class RatingTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', password='testpass')
        self.user2 = CustomUser.objects.create_user(username='testuser2', password='testpass')
        self.post = Post.objects.create(user=self.user, content='content')
        self.evidence = Evidence.objects.create(user=self.user, post=self.post, text='text')
        self.url = reverse('evidence_detail', args=[self.evidence.id])

    def test_evidence_retrieval(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['evidence'], self.evidence)

    def test_404_for_nonexistent_evidence(self):
        url = reverse('evidence_detail', args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_user_has_rated(self):
        EvidenceRating.objects.create(evidence=self.evidence, user=self.user, post=self.post, star_count=4)
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url)
        self.assertTrue(response.context['user_has_rated'])

    def test_average_rating_calculation(self):
        EvidenceRating.objects.create(evidence=self.evidence, post=self.post, user=self.user, star_count=4)
        EvidenceRating.objects.create(evidence=self.evidence, post=self.post, user=self.user2, star_count=5)
        response = self.client.get(self.url)
        self.assertEqual(response.context['rounded_avg'], 4.5)

    def test_template_rendering(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'evidence_detail.html')

class NotificationModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', password='testpass')

    def test_notification_creation(self):
        notification = Notification.objects.create(user=self.user, content='Test Content')
        self.assertIsInstance(notification, Notification)

class NotificationViewTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', password='testpass')
        self.notifications = [Notification.objects.create(user=self.user, content=f'Test Content {i}') for i in range(20)]
        Profile.objects.create(user=self.user, username='username', content='content')

    def test_pagination(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('notification'))
        self.assertEqual(len(response.context['page_obj']), 10)
