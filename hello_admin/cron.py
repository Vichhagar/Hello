import logging
from django_cron.cron import CronJobBase, Schedule
from datetime import timedelta
from django.utils import timezone
from hello_public.models import Post

class DeleteOldPosts(CronJobBase):
    RUN_EVERY_MINS = 1
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'hello_admin.cron.DeleteOldPosts'

    def job(self):
        print('cron running...')
        logger = logging.getLogger(__name__)
        ninety_days_ago = timezone.now() - timedelta(days=1)
        in_bin_posts = Post.objects.filter(postStatus='in_bin', postDate__lte=ninety_days_ago)
        num_deleted = in_bin_posts.count()
        in_bin_posts.delete()
        logger.info(f"{num_deleted} posts deleted on {timezone.now().date()}")
        logger.info(f"hello")
