from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class File(models.Model):
    title = models.CharField(max_length=64)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(null=True, blank=True)
    lang = models.CharField(max_length=64, null=True, blank=True)
    info = models.TextField(null=True, blank=True)
    creation_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    linkedto = models.ForeignKey(File, on_delete=models.CASCADE)
    comment = models.TextField()
    parentComment = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )
    creation_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.username


class ResetCodes(models.Model):
    user = models.ForeignKey(User, unique=True, on_delete=models.CASCADE)
    code = models.CharField(max_length=25)
    creation_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.username
