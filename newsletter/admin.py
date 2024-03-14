from django.contrib import admin
from .models import Subscriber


class SubscriberAdmin(admin.ModelAdmin):
    list_display = (
        'email',
        'verified',
    )


admin.site.register(Subscriber, SubscriberAdmin)
