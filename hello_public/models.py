from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.contrib.auth.hashers import make_password
import uuid
import hashlib
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

    
class RegistrationToken(models.Model):
    hashed_email = models.CharField(max_length=255, unique=True)
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    used = models.BooleanField(default=False)
    
class User(AbstractUser):
    USER_TYPE = [
        ('admin', 'admin'),
        ('moderator', 'moderator'),
        ('official', 'official'),
        ('normal', 'normal'),
    ]

    profileImage = models.ImageField(upload_to='profiles/', null=True, blank=True)
    userType = models.CharField(max_length=10, choices=USER_TYPE, default='normal')
    userBio = models.CharField(max_length=100, null=True, blank=True)
    is_banned = models.BooleanField(null=True, default=False)

    def __str__(self):
        return f'{self.username} | {self.id}'
    
    def send_password_reset_email(self, domain):
        subject = 'Reset your password'
        message = f'Click the following link to reset your password: {domain}/reset_password/'
        from_email = settings.DEFAULT_FROM_EMAIL
        # recipient_list = [self.email]
        recipient_list = ['greenraysvich@gmail.com']
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)

class Activity(models.Model):
    activityOrganizer = models.ForeignKey(User, on_delete=models.CASCADE)
    activityTitle = models.CharField(max_length=50)
    activityLocation = models.CharField(max_length=100)
    activityDiscription = models.TextField()
    activityDate = models.DateTimeField()
    activityOpenDate = models.DateTimeField()
    activityCloseDate = models.DateTimeField()
    activityCreateDate = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.id} organized by {self.activityOrganizer}"

class ActivityParticepationList(models.Model):
    class Meta:
        unique_together = (('userId', 'activityId'),)

    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    activityId = models.ForeignKey(Activity, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.userId} join {self.activityId}"

# class DiscussionRoom(models.Model):
#     roomName = models.CharField(max_length=50)

#     def __str__(self):
#         return f"{self.roomName}"

class Discussion(models.Model):
    messageDate = models.DateTimeField(default=timezone.now)
    message = models.TextField()
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    activityId = models.ForeignKey(Activity, on_delete=models.CASCADE)

class Post(models.Model):
    POST_STATUS = [
        ('in_bin', 'in_bin'),
        ('live', 'live'),
        ('draft', 'draft'),
        ('ban', 'ban'),
    ]

    POST_TYPE = [
        ('normal', 'normal'),
        ('anonymous', 'anonymous')
    ]

    postType = models.CharField(max_length=20, choices=POST_TYPE, null=True)
    postDate = models.DateTimeField(default=timezone.now)
    postText = models.TextField()
    postStatus = models.CharField(max_length=10, choices=POST_STATUS, default='live')
    approveBy = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='moderator')
    # is_ban = models.BooleanField(null=False)
    disable_comment = models.BooleanField(null=True)
    userId = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.postText}"

class Image(models.Model):
    imageLink = models.ImageField(upload_to='post/')
    postId = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.imageLink}"

class Like(models.Model):
    postId = models.ForeignKey(Post, on_delete=models.CASCADE)
    userId = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.userId} like {self.postId}"

class Comment(models.Model):
    conmmentTime = models.DateTimeField(default=timezone.now)
    commmentText = models.TextField()
    isEdited = models.BooleanField(default=False)
    postId = models.ForeignKey(Post, on_delete=models.CASCADE)
    userId = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.commmentText}"

class Reply(models.Model):
    replyTime = models.DateTimeField(default=timezone.now)
    replyText = models.TextField()
    isEdited = models.BooleanField(default=False)
    conmmentId = models.ForeignKey(Comment, on_delete=models.CASCADE)
    userId = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.replyText}"

class Save(models.Model):
    postId = models.ForeignKey(Post, on_delete=models.CASCADE)
    userId = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.userId} save {self.postId}"

class Notification(models.Model):
    NOTIFICATION_STATUS = [
        ('unread', 'unread'),
        ('read', 'read')
    ]

    NOTIFICATION_TYPE = [
        ('activity_start', 'activity_start'),
        ('activity_join', 'activity_join'),
        ('like', 'like'),
        ('comment', 'comment'),
        ('reply', 'reply'),
        ('new_post', 'new_post'),
        ('message', 'message'),
        ('report', 'report'),
    ]

    NOTIFICATION_ON = [
        ('post', 'post'),
        ('activity', 'activity'),
    ]

    notificationTime = models.DateTimeField(auto_now=True)
    notificationStatus = models.CharField(max_length=10, choices=NOTIFICATION_STATUS, default='unread')
    notificationOn = models.CharField(max_length=10, choices=NOTIFICATION_ON, null=True)
    notificationType = models.CharField(max_length=20, choices=NOTIFICATION_TYPE)
    notificationLink = models.TextField() 
    notificationMessage = models.TextField(null=True) 
    notificationSender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    notificationReceiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_notifications')


    def __str__(self):
        return f"{self.notificationOn}: {self.notificationLink}"
    

class IgnoreNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ignored_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ignored_by')
    created_at = models.DateTimeField(auto_now_add=True)

class ReportPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    postId = models.ForeignKey(Post, on_delete=models.CASCADE)
    Reason = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class ActivityLocation(models.Model):
    location_name = models.TextField()
    frequency = models.BigIntegerField(null=True, default=0)