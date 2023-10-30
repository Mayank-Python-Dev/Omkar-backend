from django.contrib import admin
from .models import (
    RentalNotification
)
# Register your models here.



class RentalNotificationAdmin(admin.ModelAdmin):
     model=RentalNotification
     list_display = ['uid','rental','status',"message","get_date_time"]

admin.site.register(RentalNotification,RentalNotificationAdmin)