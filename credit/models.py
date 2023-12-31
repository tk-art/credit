from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime

class CustomUser(AbstractUser):
  pass

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    username = models.CharField(max_length=100)
    backimage = models.ImageField(upload_to='item_images/', null=True, blank=True)
    image = models.ImageField(upload_to='item_images/', null=True, blank=True)
    content = models.TextField()
    follows = models.ManyToManyField('self', related_name='followed_by', symmetrical=False)

class Post(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    deadline = models.DateTimeField(default=datetime.now)
    image = models.ImageField(upload_to='item_images/', null=True, blank=True)
    content = models.TextField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)
    like_count = models.PositiveIntegerField(default=0)

class Like(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    is_liked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Evidence(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post = models.OneToOneField(Post, on_delete=models.CASCADE)
    text = models.TextField(max_length=300)
    timestamp = models.DateTimeField(auto_now_add=True)

class EvidenceImage(models.Model):
    evidence = models.ForeignKey(Evidence, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='item_images/')

class EvidenceRating(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    evidence = models.ForeignKey(Evidence, on_delete=models.CASCADE)
    star_count = models.IntegerField(default=0)
    text = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
