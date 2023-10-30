
import uuid
from django.db import models
from .user_managers import (
    UserManager
)
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from warehouse.models import (
    Company,
    Property
)

from django.urls import reverse

type_choice = (
    ("android","android"),
    ("web","web")
)

class User(AbstractUser):
    username = models.CharField(max_length=256)
    user_uid = models.UUIDField(default=uuid.uuid4, editable=False, blank=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=200,default = "")
    last_name = models.CharField(max_length=200,default = "")
    phone = models.CharField(_("Phone"),max_length=50,default="",unique=True)
    address = models.TextField(default="")
    city = models.CharField(max_length=200,default="")
    zip_code = models.CharField(max_length=100,default="")
    birth_date = models.DateField(blank=True, null=True)
    app_type = models.CharField(max_length=26,default="android",choices=type_choice)
    profile = models.ImageField(upload_to='image',default="image/user-logo.png")
    belong_to = models.ManyToManyField(Company,blank=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True,null=True)
    

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username',)
    objects = UserManager()

    # class UniqueConstraint(self,fields):
    #     return super()

    class Meta:
        verbose_name_plural = "User"
        # constraints = [
        #     models.UniqueConstraint(fields=['room', 'date'], name='unique_booking')
        # ]

    def __str__(self):
        return self.username
    
    @property
    def get_groups(self):
        get_group_name = self.groups.first().name
        return get_group_name



# def build_url_for_user(*args, **kwargs):
#         get = kwargs.pop('get', {})
#         url = reverse(*args, **kwargs)
#         if get:
#             url += '?' + urllib.parse.urlencode(get)
#         return url

class InvestorManager(UserManager):
    def get_queryset(self):
        return super(InvestorManager, self).get_queryset().filter(
            groups__name='Investor')

class Investor(User):
    objects = InvestorManager()
    class Meta:
        proxy = True
        verbose_name_plural= 'Investor'
    
    def get_investor_url(self):
        return reverse('get-contract-investor-detail', kwargs = {"uuid":self.user_uid})
        # get_group_name = self.groups.first()
        # url = build_url_for_user('get-contract-detail', kwargs = {"uuid":self.user_uid},get={'group_type': get_group_name.name})
        # return url
    
    
class RentalManager(UserManager):
    def get_queryset(self):
        return super(RentalManager, self).get_queryset().filter(
            groups__name='Rental')

class Rental(User):
    objects = RentalManager()
    class Meta:
        proxy = True
        verbose_name_plural = 'Rental'
    
    def get_investor_url(self):
        return reverse('get-contract-rental-detail', kwargs = {"uuid":self.user_uid})
    
    # @property
    # def get_total_warehouse(self):
    #     try:
    #         get_total_number_of_warehouse = Rental.objects.filter(rental_contract__user__user_uid='51f9c7eb-8f1b-4fcc-9124-58831235d387').count()
    #         return get_total_number_of_warehouse
    #     except Exception as exception:
    #         return str(exception)
    

class UserAndInvestorManager(UserManager):
    def get_queryset(self):
        return super(UserAndInvestorManager, self).get_queryset().exclude(
            groups__name='Rental')

class UserAndInvestor(User):
    objects = UserAndInvestorManager()
    class Meta:
        proxy = True
        verbose_name_plural= 'Users and Investors'
    
    @property
    def get_groups(self):
        get_group_name = self.groups.first().name
        return get_group_name


class FarmerManager(UserManager):
    def get_queryset(self):
        return super(FarmerManager,self).get_queryset().filter(
            groups__name='Farmer')

class Farmer(User):
    objects =FarmerManager()
    class Meta:
        proxy = True
        verbose_name_plural= 'Farmer'

    def get_farmer_url(self):
        return reverse('get-contract-farmer-detail', kwargs = {"uuid":self.user_uid})

class OwnerManager(UserManager):
    def get_queryset(self):
        return super(OwnerManager,self).get_queryset().filter(
            groups__name='Owner')

class Owner(User):
    objects =OwnerManager()
    class Meta:
        proxy = True
        verbose_name_plural= 'Owner'
    

    # def get_farmer_url(self):
    #     return reverse('get-contract-farmer-detail', kwargs = {"uuid":self.user_uid})
