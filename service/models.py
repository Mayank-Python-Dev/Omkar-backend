from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from account.models import (
    User,
    Rental
)
import uuid,string,random
from datetime import datetime
from warehouse.models import (
    Gala,
    
)
from django.utils import timezone
import math
from django.shortcuts import get_object_or_404
from datetime import date
from django.core.validators import FileExtensionValidator
import os 
from contract.models import (
    Rental as ContractRental
)
# Create your models here.

class BaseModel(models.Model):
    service_uid = models.UUIDField(default=uuid.uuid4, editable=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class Service(BaseModel):
    service_name = models.CharField(max_length=100,blank=True, null=True)
     
    class Meta:
        # verbose_name = _('Service')
        verbose_name_plural = _('Service') 

    def __str__(self):
        return "{}".format(self.service_name)
    
class SubService(BaseModel):
    service = models.ForeignKey(Service,on_delete=models.CASCADE)
    sub_service_name = models.CharField(_("sub service name"),max_length=100,blank=True, null=True)

    class Meta:
        verbose_name_plural = _('Sub Service')
    
    def __str__(self):
        return "{}".format(self.sub_service_name)


status_choices=(
    ('Pending','Pending'),
    ('Accepted','Accepted'),
    ('In-progress','In-progress'),
    ('Completed','Completed'),
    ('Reject','Reject'),
)
class ServiceRequest(BaseModel):
    tracking_id=models.CharField(max_length=11,null=True,blank=True)
    user =models.ForeignKey(Rental,on_delete=models.CASCADE)
    request_sub_service=models.ForeignKey(SubService,on_delete=models.CASCADE,related_name='get_service')
    gala =models.ForeignKey(Gala,on_delete=models.CASCADE)
    service_request_date = models.DateTimeField(blank=True ,null=True)
    status=models.CharField(_("status"),choices= status_choices,max_length=50,default='Pending')
    description=models.TextField(null=True,blank=True)

    class Meta:
        verbose_name_plural = _('Service Request')
    
    def __str__(self):
        return "{}".format(self.user)
    
    @property
    def get_service_date(self):
        return datetime.strptime(str(self.service_request_date.date),"%Y-%m-%d").strftime("%d-%m-%Y")
    
    # @property
    # def get_service_request_name(self):
    #     return self.service_request.sub_service_name
        

    # def get_service_request_detail_url(self):
    #     get_user_uid = get_object_or_404(Rental,user_uid=self.user.user_uid)
    #     return reverse("get-rental-request-details",kwargs={"user_uid":get_user_uid.user_uid,"tracking_id":self.tracking_id})

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

        get_date=self.service_request_date
        service_request_date = (datetime.strftime(get_date, "%d-%b-%Y "))
        return service_request_date
            


    def get_status(self):
        if self.status=='Accepted':

            return "Your Request has been submitted successfully!"
        elif self.status=='Reject':
             return "Your Request has been Rejected!"
        elif self.status == 'Completed':
            return "Your Request has been Completed successfully!"
        else:
            return "Your Request has been pending!"
        return self.status
        
    def save(self, *args, **kwargs):
        N = 7
        res = ''.join(random.choices(string.ascii_uppercase, k=N))
        year = str(date.today().year)
        self.tracking_id = year + res
        super(ServiceRequest, self).save(*args, **kwargs)

    
def upload_to_service_image(instance, filename):
    get_profile_instance = get_object_or_404(User,id=instance.service_request.user.id)
    return os.path.join(str(get_profile_instance.user_uid), 'image', filename)

class Image(BaseModel):
    service_request=models.ForeignKey(ServiceRequest,on_delete=models.CASCADE,related_name="service_request_images")
    image=models.ImageField(upload_to= upload_to_service_image,null=True,validators=[FileExtensionValidator(allowed_extensions=['jpg','jpeg','png'])])

    def __str__(self):
        return "{}".format(self.image)
    
    class Meta:
        verbose_name_plural = _('Service Request Image')



class RepairRequest(BaseModel):
    user =models.ForeignKey(Rental,on_delete=models.CASCADE)
    gala = models.ForeignKey(Gala,on_delete=models.CASCADE)
    description = models.TextField()


    def __str__(self):
        return self.user.username
    
    class Meta:
        verbose_name_plural = _('Repair Request')


def upload_to_request_image(instance, filename):
    get_profile_instance = get_object_or_404(User,id=instance.repair_request.user.id)
    return os.path.join(str(get_profile_instance.user_uid), 'image', filename)


# class RepairRequestImage(BaseModel):
#     repair_request=models.ForeignKey(RepairRequest,on_delete=models.CASCADE)
#     image=models.ImageField(upload_to= upload_to_request_image,null=True,validators=[FileExtensionValidator(allowed_extensions=['jpg','jpeg','png'])])

#     def __str__(self):
#         return "{}".format(self.image)
    
#     class Meta:
#         verbose_name_plural = _('Repair Request Image')



leave_request_status_choices=(
    ('Pending','Pending'),
    ('Approved','Approved'),
    ('Reject','Reject'),
)

class LeaveGalaRequest(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, blank=True)
    user =models.ForeignKey(Rental,on_delete=models.CASCADE,related_name='user_leave_request')
    gala =models.ForeignKey(Gala,on_delete=models.CASCADE,related_name = 'user_gala_leave_request')
    reason_for_leaving = models.TextField(default = "")
    status=models.CharField(_("status"),choices= leave_request_status_choices,max_length=50,default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return "{}".format(self.user)
    
    # def save(self, *args, **kwargs):
    #     if self.status == "Approved":
    #         get_contract_rental = ContractRental.objects.get(gala_id = self.gala.id)
    #         get_contract_rental.delete()
    #     super(LeaveGalaRequest,self).save(*args, **kwargs)


renew_request_status_choices=(
    ('Pending','Pending'),
    ('Approved','Approved'),
    ('Reject','Reject'),
)

class RenewGalaRequest(models.Model):
    renew_uid = models.UUIDField(default=uuid.uuid4, editable=False, blank=True)
    renew_user = models.ForeignKey(Rental,on_delete=models.CASCADE,related_name='user_renew_request')
    renew_gala = models.ForeignKey(Gala,on_delete=models.CASCADE,related_name = 'gala_renew_request')
    renew_status = models.CharField(_("status"),choices= renew_request_status_choices,max_length=50,default='Pending')
    renew_created_at = models.DateTimeField(auto_now_add=True)
    renew_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Renew Gala Request"

    def __str__(self):
        return "{} {}".format(self.renew_user.username,self.renew_gala)