from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import *

@receiver(pre_delete, sender=User)
def user_delete_callback(sender, instance, **kwargs):
    # Get all the posts associated with this user
    user_posts = Post.objects.filter(userId=instance)

    # Update the postStatus for all the posts
    for post in user_posts:
        post.postStatus = 'in_bin'
        post.save()

@receiver(pre_delete, sender=User)
def delete_registration_token(sender, instance, **kwargs):
    print("Deleting registration token...")
    hashed_email = hashlib.sha256(instance.email.encode()).hexdigest()
    try:
        token = RegistrationToken.objects.get(hashed_email=hashed_email)
        token.delete()
    except RegistrationToken.DoesNotExist:
        pass
