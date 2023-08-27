from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
  pass

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    username = models.CharField(max_length=100)
    backimage = models.ImageField(upload_to='item_images/', null=True, blank=True)
    image = models.ImageField(upload_to='item_images/', null=True, blank=True)
    content = models.TextField()

class Post(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)
