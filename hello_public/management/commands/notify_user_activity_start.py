from django.core.management import call_command
from django.core.management.base import BaseCommand
from hello_public.models import *
from datetime import timedelta, date
from django.utils import timezone
import datetime
import pytz


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        tz = pytz.timezone('Asia/Bangkok')
        now = datetime.datetime.now(tz)
        tomorrow = now + datetime.timedelta(days=1)
        day_after_tomorrow = now + datetime.timedelta(days=2)

        activities = Activity.objects.filter(
            activityDate__gte=tomorrow,
            activityDate__lt=day_after_tomorrow
        )

        print('notification cron run...')

        for activity in activities:
            participants = ActivityParticepationList.objects.filter(activityId=activity).values_list('userId', flat=True)
            print('notification cron run...')
            
            for participant_id in participants:
                notification = Notification(
                    notificationOn='activity',
                    notificationType='activity_start',
                    notificationLink=activity.id,
                    notificationSender=activity.activityOrganizer,
                    notificationReceiver=User.objects.get(id=participant_id)
                )
                notification.save()
