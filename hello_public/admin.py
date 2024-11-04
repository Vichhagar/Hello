from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(Activity)
admin.site.register(ActivityParticepationList)
# admin.site.register(DiscussionRoom)
admin.site.register(Discussion)
admin.site.register(Post)
admin.site.register(Image)
admin.site.register(Like)
admin.site.register(Comment)
admin.site.register(Reply)
admin.site.register(Save)
admin.site.register(Notification)
admin.site.register(RegistrationToken)
admin.site.register(IgnoreNotification)
admin.site.register(ReportPost)
admin.site.register(ActivityLocation)
