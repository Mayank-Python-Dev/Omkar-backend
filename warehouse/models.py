import uuid, random, urllib
from django.db import models
from django.utils.translation import gettext_lazy as _
import warehouse.helpers
from django.urls import reverse
from django.core.validators import MaxValueValidator, MinValueValidator 
from  account import models as AccountModels
# from contract import models as ContractModels
import contract

# Create your models here.


class PROPERTY_TYPE(models.TextChoices):
    PEB = 'PEB'
    COLD_STORAGE  = 'COLD_STORAGE'
    RCC = 'RCC'
    SHED = 'SHED'
    OTHER = 'OTHER'

# PROPERTY_TYPE = (
#     ('PEB','PEB'),
#     ('COLD STORAGE','COLD STORAGE'),
#     ('RCC','RCC'),
#     ('SHED','SHED'),
#     ('OTHER','OTHER'),
# )

def build_url(*args, **kwargs):
    get = kwargs.pop('get', {})
    url = reverse(*args, **kwargs)
    if get:
        url += '?' + urllib.parse.urlencode(get)
    return url

class BaseModel(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


    # def save(self,*args,**kwargs):
    #     if self.uid is None:
    #         self.uid =  get_shortuuid()
    #     super(BaseModel,self).save(*args,*kwargs)
    
class Company(BaseModel):
    name = models.CharField(max_length=128)
    
    class Meta:
        ordering = ("-created_at",)
        verbose_name_plural = "Company"
    
    def __str__(self):
        return self.name.upper()

    def get_tenant_url(self):
        url = build_url('get-investors-warehouses', get={'company_type': self.name})
        return url


class Property(BaseModel):
    company = models.ForeignKey(Company,on_delete=models.CASCADE,related_name='get_properties')
    property_name = models.CharField(max_length=256,default="")
    property_type = models.CharField(_("warehouse type"),max_length=200,choices=PROPERTY_TYPE.choices)
    property_survey_number = models.CharField(max_length=36,unique=True)
    address = models.TextField()
    city = models.CharField(max_length=50)
    zipcode = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    is_allotted_to_farmer = models.BooleanField(default=False)

    
    class Meta:
        ordering = ("-created_at",)
        verbose_name_plural = "Property"
    
    def __str__(self):
        return self.property_name

    # @property
    def get_absolute_url(self):
        return reverse("get-leave-and_license-detail",kwargs={"uuid":self.uid})
        
    # @property
    # def get_gala_url(self):
    #     return reverse("get-gala-with-property-uid",kwargs = {"property_uid":str(self.uid)})

    @property
    def total_gala(self):
        try:
            print(self)
            total_count = self.get_gala.count()
            return total_count
        except Exception as exception:
            return 0
    
    @property
    def get_owner_type(self):
        if not self.is_allotted_to_farmer:
            get_owner = AccountModels.Owner.objects.first().username
            return F"{get_owner} (Developer)"
        else:
            get_owner = contract.models.Farmer.objects.get(warehouse__uid = self.uid).user.username
            return F"{get_owner} (Farmer)"
            
# @classmethod
# def get_property_name(cls):
#     return cls.property_name

class Gala(BaseModel):
    warehouse = models.ForeignKey(Property,on_delete=models.CASCADE,related_name="get_gala")
    gala_number = models.CharField(max_length=200,unique=True)
    gala_area_size = models.DecimalField(default=0,max_digits=6, decimal_places=2)
    gala_price = models.DecimalField(default=0,max_digits=6, decimal_places=2)
    is_allotted = models.BooleanField(default=False)
    is_allotted_to_rental = models.BooleanField(default=False)
    is_allotted_to_farmer = models.BooleanField(default=False)
    
    class Meta:
        ordering = ("-created_at",)
        verbose_name_plural = "Gala"
    
    def __str__(self):
        return self.gala_number


    @property
    def get_owner_type(self):
        if not self.is_allotted_to_farmer:
            get_owner = AccountModels.Owner.objects.first().username
            return F"{get_owner} (Developer)"
        else:
            get_owner = contract.models.Farmer.objects.get(warehouse__uid = self.warehouse__uid).user.username
            return F"{get_owner} (Farmer)"


    def save(self, *args, **kwargs):
        try:
            get_warehouse_instance  = Property.objects.get(uid = self.warehouse.uid)
            if get_warehouse_instance.is_allotted_to_farmer == True:
                self.is_allotted_to_farmer = True
            super(Gala, self).save(*args, **kwargs)
        except Exception as exception:
            pass



