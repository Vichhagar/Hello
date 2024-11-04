from django import template
from django.utils.timesince import timesince
from datetime import datetime, timedelta

register = template.Library()

@register.filter
def date_filter(value):
    now = datetime.now()
    diff = now - value

    if diff < timedelta(minutes=60):
        return f"{diff.seconds//60} min ago"
    elif diff < timedelta(days=1):
        return f"{diff.seconds//3600} hour ago"
    elif diff < timedelta(weeks=1):
        return f"{diff.days} days ago"
    else:
        return f"{diff.days//7} weeks ago"
