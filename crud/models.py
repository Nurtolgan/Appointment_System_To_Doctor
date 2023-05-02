from datetime import datetime

from django.db import models
from django.utils import timezone

from users.models import CustomUser


class Post(models.Model):
    first_name = models.CharField(max_length=40, blank=False, default='')
    last_name = models.CharField(max_length=40, blank=False, default='')
    image = models.ImageField(upload_to='images/', default='images/default.jpg')
    speciality = models.CharField(max_length=40, blank=False, default='')
    experience = models.PositiveIntegerField(blank=False, default=0)
    phone = models.CharField(max_length=11, blank=False, default='')
    email = models.EmailField(max_length=150, blank=False, default='')
    location = models.CharField(max_length=70, blank=False, default='')
    education = models.CharField(max_length=200, blank=False, default='')
    procedure = models.CharField(max_length=300, blank=False, default='')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return self.first_name


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)
    sentiment = models.CharField(max_length=1, blank=False, default='O')
    sentiment_score = models.FloatField(blank=False, default=0.0)
    class Meta:
        ordering = ['created_on']

    def __str__(self):
        return 'Comment {} by {}'.format(self.body, self.name)


class TranslatedComment(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE,related_name='translated_comments')
    translated_body = models.TextField(default='')


class Zapis(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name='appointments')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    time_slot = models.CharField(max_length=5, choices=(('9:00', '9:00'), ('10:00', '10:00'), ('11:00', '11:00'), ('12:00', '12:00'), ('14:00', '14:00'), ('15:00', '15:00'), ('16:00', '16:00'), ('17:00', '17:00')))
    date = models.DateField()
    is_approved = models.BooleanField(default=False)

    @property
    def is_expired(self):
        now = timezone.now()
        appointment_datetime = datetime.combine(self.date, self.time_slot)
        return appointment_datetime < now

