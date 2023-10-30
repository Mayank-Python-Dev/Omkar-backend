from django.db import models
from account.models import (
    Rental
)
import uuid,math
from datetime import datetime
from django.utils import timezone
from warehouse.models import (
    Gala
)
from bulk_update_or_create import BulkUpdateOrCreateQuerySet

# Create your models here.

request_status = (
    ('Leave_Gala','Leave_Gala'),
    ('Service_Gala','Service_Gala'),
    ('Renew_Gala','Renew_Gala'),
)

class BaseModel(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class RentalNotification(BaseModel):
    objects = BulkUpdateOrCreateQuerySet.as_manager()
    rental = models.ForeignKey(Rental,on_delete=models.CASCADE)
    gala = models.ForeignKey(Gala,on_delete=models.CASCADE,null=True,blank=True)
    status = models.CharField(choices= request_status,max_length=50,default='')
    sub_service_name = models.CharField(max_length=100,null=True,blank=True,default = "")
    is_seen = models.BooleanField(default=False)
    message = models.TextField()

    class Meta:
        verbose_name_plural = "Rental Notification"

    def __str__(self):
        return f"{self.rental.first_name} {self.rental.last_name}"
    
    def get_date_time(self):
 
        now = timezone.now()
        diff=now-self.created_at

        if diff.days == 0 and diff.seconds >= 0 and diff.seconds < 60:
            seconds= diff.seconds
            if seconds == 1:
                return str(seconds) + "second ago"
            else:
             return str(seconds) + " seconds ago"

        if diff.days == 0 and diff.seconds >= 60 and diff.seconds < 3600:
            minutes= math.floor(diff.seconds/60)
            if minutes == 1:
                return str(minutes) + " minute ago" 
            else:
                 return str(minutes) + " minutes ago"

        if diff.days == 0 and diff.seconds >= 3600 and diff.seconds < 86400:
            hours= math.floor(diff.seconds/3600)

            if hours == 1:
                return str(hours) + " hour ago"

            else:
                return str(hours) + " hours ago"
            
        

        if diff.days >= 30 and diff.days < 365:
            months= math.floor(diff.days/30)
            

            if months == 1:
                return str(months) + " month ago"

            else:
                return str(months) + " months ago"

        get_date=self.created_at
        get_created_at = (datetime.strftime(get_date, "%d-%b-%Y"))
        return get_created_at
    
    # def get_message(self):
    #     if self.status == "Service_Gala":
    #         message = f"{self.rental.first_name} {self.rental.last_name} has requested for {self.sub_service_name} on {self.gala.gala_number} ({self.gala.warehouse.property_name})"
    #     else:
    #         message = f"{self.rental.first_name} {self.rental.last_name} wants to leave gala {self.gala.gala_number} ({self.gala.warehouse.property_name})"
    #     return message