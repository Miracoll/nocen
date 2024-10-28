from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from uuid import uuid4

# Create your models here.

class User(AbstractUser):
    last_login_ip = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(max_length=10, default='user')
    ref = models.UUIDField(default=uuid4, editable=False)

class Log(models.Model):
    action = models.CharField(max_length=2000)
    is_success = models.BooleanField(default=True)
    ip_address = models.CharField(max_length=20, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    created = models.DateTimeField(default=timezone.now)
    ref = models.UUIDField(default=uuid4, editable=False)

    def __str__(self):
        return f'{self.action} by {self.user.last_name}'