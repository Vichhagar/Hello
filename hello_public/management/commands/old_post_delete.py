from django.core.management import call_command
from django.core.management.base import BaseCommand
from hello_public.models import *
from datetime import timedelta, date

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        today = date.today()
        posts = Post.objects.filter(postStatus='in_bin')
        print('post cron run...')

        for post in posts:
            start_date = post.postDate.date()
            end_date = start_date + timedelta(days = 90)
            if end_date < today:
                Post.objects.get(pk=post.id).delete()