import uuid,os,shutil 

from django.conf import settings
from django.db import models
from warehouse.models import (
    Gala,
    Property
)
# from contract.models import (
#     Rental as ContractRental
# )
from account.models import (
    User,
    Investor as AccountInvestor,
    Rental as AccountRental,
    Rental,
    UserAndInvestor,
    Farmer as AccountFarmer,
    Owner
)
import datetime
from django.forms import ValidationError as FormValidationError
from polymorphic.models import PolymorphicModel
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator


# Create your models here.

def build_url(*args, **kwargs):
    get = kwargs.pop('get', {})
    url = reverse(*args, **kwargs)
    if get:
        url += '?' + urllib.parse.urlencode(get)
    return url


def get_main_owner():
    get_main_owner = User.objects.get(is_superuser=True)
    return get_main_owner.pk

class AgreementType(models.TextChoices):
    Saledeed = "Saledeed"
    Leave_and_License = "Leave_and_License"
    Development = "Development"

class Contract(PolymorphicModel):
    uid = models.UUIDField(default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name_plural = "Contract"
    
    def __str__(self):
        return "{}".format(self.uid)



def upload_to_investor_user_aggreement_valid_doc(instance,filename):
    get_rental_user_instance = get_object_or_404(AccountInvestor,id=instance.user.id)
    get_owner_instance = get_object_or_404(Owner , id = instance.owner.id)
    # get_contract_instance = get_object_or_404(Rental,id = instance.id)
    string_formatter = f"{get_owner_instance.username} - {get_rental_user_instance.username} ({instance.uid})"
    get_aggreement_type_instance = f"{instance.agreement_type}"


    # check_directory_flag  = str(settings.BASE_DIR) + "/media" + "/Leave_and_License/" + string_formatter + "/aggreement_valid_doc/"
    check_directory_flag  = os.path.join(str(settings.BASE_DIR) , "media" , "Saledeed" , string_formatter , "aggreement_valid_doc/")
    if os.path.isdir(check_directory_flag):
        # get_media_path = os.path.join(settings.BASE_DIR,"media/" ,"Leave_and_License/" + string_formatter + "/" + "aggreement_valid_doc/")
        get_media_path = os.path.join(settings.BASE_DIR,"media" ,"Saledeed" , string_formatter , "aggreement_valid_doc/")
        get_length_of_files = len(os.listdir(get_media_path))
        if get_length_of_files >= 1:
            shutil.rmtree(get_media_path)
    return os.path.join(get_aggreement_type_instance,string_formatter,"aggreement_valid_doc",filename)


def upload_to_investor_user_ghar_patti_doc(instance,filename):
    get_rental_user_instance = get_object_or_404(AccountInvestor,id=instance.user.id)
    get_owner_instance = get_object_or_404(Owner , id = instance.owner.id)
    # get_contract_instance = get_object_or_404(Rental,id = instance.id)
    string_formatter = f"{get_owner_instance.username} - {get_rental_user_instance.username} ({instance.uid})"
    get_aggreement_type_instance = f"{instance.agreement_type}"


    # check_directory_flag  = str(settings.BASE_DIR) + "/media" + "/Leave_and_License/" + string_formatter + "/ghar_patti_doc/"
    check_directory_flag  = os.path.join(str(settings.BASE_DIR) , "media" , "Saledeed" , string_formatter , "ghar_patti_doc/")
    if os.path.isdir(check_directory_flag):
        # get_media_path = os.path.join(settings.BASE_DIR,"media/" ,"Leave_and_License/" + string_formatter + "/" + "ghar_patti_doc/")
        get_media_path = os.path.join(settings.BASE_DIR,"media" ,"Saledeed" , string_formatter ,  "ghar_patti_doc/")

        get_length_of_files = len(os.listdir(get_media_path))
        if get_length_of_files >= 1:
            shutil.rmtree(get_media_path)
    return os.path.join(get_aggreement_type_instance,string_formatter,"ghar_patti_doc",filename)


class Investor(Contract):
    gala = models.OneToOneField(Gala,on_delete=models.CASCADE,related_name="gala_investor_contract_detail",null=True)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE,default=get_main_owner,related_name="get_owner_contract")
    user = models.ForeignKey(AccountInvestor, on_delete=models.CASCADE,related_name="investor_contract")
    agreement_type = models.CharField(max_length=255,default=AgreementType.Saledeed) # 24/01/2023 
    agreement_valid_doc = models.FileField(max_length = 255,upload_to=upload_to_investor_user_aggreement_valid_doc,validators=[FileExtensionValidator(['pdf'])], blank=True, null=True)
    ghar_patti_doc = models.FileField(max_length = 255 ,upload_to=upload_to_investor_user_ghar_patti_doc,validators=[FileExtensionValidator(['pdf'])],blank=True,null=True)
    ghar_patti_start_date = models.DateField(editable=True,default=datetime.date.today)
    ghar_patti_end_date = models.DateField(editable = True ,blank=True,null=True)


    class Meta:
        verbose_name_plural = "Contract With Investor"

    def __str__(self):
        return "{}".format(self.agreement_type)

    
    def clean(self, *args, **kwargs):
        get_gala_instance = get_object_or_404(Gala,uid = self.gala.uid)
        if get_gala_instance.is_allotted_to_rental == True:
            raise ValidationError(
                "You have already allotted this gala to Rental"
                )
        elif get_gala_instance.is_allotted_to_farmer == True:
            raise ValidationError(
                "You have already allotted this gala to Farmer"
                )
        return super(Investor, self).clean(*args, **kwargs)


    def save(self, *args, **kwargs):
        self.clean()
        print(self.gala.uid)
        get_gala_instance = get_object_or_404(Gala,uid = self.gala.uid)
        get_gala_instance.is_allotted = True
        get_gala_instance.save()
        super(Investor, self).save(*args, **kwargs)
    

    def delete(self, *args, **kwargs):
        print(self.gala.uid)
        get_gala_instance = get_object_or_404(Gala,uid = self.gala.uid)
        get_gala_instance.is_allotted = False
        get_gala_instance.save()
        super(Investor, self).delete()


def upload_to_farmer_user_aggreement_valid_doc(instance,filename):
    get_rental_user_instance = get_object_or_404(AccountFarmer,id=instance.user.id)
    get_owner_instance = get_object_or_404(User , id = instance.owner.id)
    # get_contract_instance = get_object_or_404(Rental,id = instance.id)
    string_formatter = f"{get_owner_instance.username} - {get_rental_user_instance.username} ({instance.uid})"
    get_aggreement_type_instance = f"{instance.agreement_type}"


    # check_directory_flag  = str(settings.BASE_DIR) + "/media" + "/Leave_and_License/" + string_formatter + "/aggreement_valid_doc/"
    check_directory_flag  = os.path.join(str(settings.BASE_DIR) , "media" , "Development" , string_formatter , "aggreement_valid_doc/")
    if os.path.isdir(check_directory_flag):
        # get_media_path = os.path.join(settings.BASE_DIR,"media/" ,"Leave_and_License/" + string_formatter + "/" + "aggreement_valid_doc/")
        get_media_path = os.path.join(settings.BASE_DIR,"media" ,"Development" , string_formatter , "aggreement_valid_doc/")
        get_length_of_files = len(os.listdir(get_media_path))
        if get_length_of_files >= 1:
            shutil.rmtree(get_media_path)
    return os.path.join(get_aggreement_type_instance,string_formatter,"aggreement_valid_doc",filename)


def upload_to_farmer_user_ghar_patti_doc(instance,filename):
    get_rental_user_instance = get_object_or_404(AccountFarmer,id=instance.user.id)
    get_owner_instance = get_object_or_404(User , id = instance.owner.id)
    # get_contract_instance = get_object_or_404(Rental,id = instance.id)
    string_formatter = f"{get_owner_instance.username} - {get_rental_user_instance.username} ({instance.uid})"
    get_aggreement_type_instance = f"{instance.agreement_type}"


    # check_directory_flag  = str(settings.BASE_DIR) + "/media" + "/Leave_and_License/" + string_formatter + "/ghar_patti_doc/"
    check_directory_flag  = os.path.join(str(settings.BASE_DIR) , "media" , "Development" , string_formatter , "ghar_patti_doc/")
    if os.path.isdir(check_directory_flag):
        # get_media_path = os.path.join(settings.BASE_DIR,"media/" ,"Leave_and_License/" + string_formatter + "/" + "ghar_patti_doc/")
        get_media_path = os.path.join(settings.BASE_DIR,"media" ,"Development" , string_formatter ,  "ghar_patti_doc/")

        get_length_of_files = len(os.listdir(get_media_path))
        if get_length_of_files >= 1:
            shutil.rmtree(get_media_path)
    return os.path.join(get_aggreement_type_instance,string_formatter,"ghar_patti_doc",filename)


class Farmer(Contract):
    warehouse = models.OneToOneField(Property,on_delete=models.CASCADE,related_name="farmer_warehouse_detail",null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE,default=get_main_owner,related_name="get_farmer_contract")
    user = models.ForeignKey(AccountFarmer, on_delete=models.CASCADE ,related_name="farmer_contract")
    agreement_type = models.CharField(max_length=255,default=AgreementType.Development)#24/01/2023
    agreement_valid_doc = models.FileField(max_length = 255,upload_to=upload_to_farmer_user_aggreement_valid_doc,validators=[FileExtensionValidator(['pdf'])], blank=True, null=True)
    ghar_patti_doc = models.FileField(max_length = 255 ,upload_to=upload_to_farmer_user_ghar_patti_doc,validators=[FileExtensionValidator(['pdf'])],blank=True,null=True)
    ghar_patti_start_date = models.DateField(editable=True,default=datetime.date.today)
    ghar_patti_end_date = models.DateField(editable = True ,blank=True,null=True)

    class Meta:
        verbose_name_plural = "Contract With Farmer"

    def __str__(self):
        return "{}".format(self.agreement_type)
    
    def save(self,*args,**kwargs):
        get_property_instance = get_object_or_404(Property,uid=self.warehouse.uid)
        get_property_instance.is_allotted_to_farmer = True
        get_property_instance.save()
        update_gala_to_farmer = Gala.objects.filter(warehouse__uid = self.warehouse.uid)
        update_gala_to_farmer.update(is_allotted_to_farmer = True)
        super(Farmer, self).save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        get_property_instance = get_object_or_404(Property,uid=self.warehouse.uid)
        get_property_instance.is_allotted_to_farmer = False
        get_property_instance.save()
        super(Farmer, self).save(*args, **kwargs)



def upload_to_rental_user_aggreement_valid_doc(instance,filename):
    get_rental_user_instance = get_object_or_404(AccountRental,id=instance.user.id)
    get_owner_instance = get_object_or_404(UserAndInvestor , id = instance.owner.id)
    # get_contract_instance = get_object_or_404(Rental,id = instance.id)
    string_formatter = f"{get_owner_instance.username} - {get_rental_user_instance.username} ({instance.uid})"
    get_aggreement_type_instance = f"{instance.agreement_type}"


    # check_directory_flag  = str(settings.BASE_DIR) + "/media" + "/Leave_and_License/" + string_formatter + "/aggreement_valid_doc/"
    check_directory_flag  = os.path.join(str(settings.BASE_DIR) , "media" , "Leave_and_License" , string_formatter , "aggreement_valid_doc/")
    if os.path.isdir(check_directory_flag):
        # get_media_path = os.path.join(settings.BASE_DIR,"media/" ,"Leave_and_License/" + string_formatter + "/" + "aggreement_valid_doc/")
        get_media_path = os.path.join(settings.BASE_DIR,"media" ,"Leave_and_License" , string_formatter , "aggreement_valid_doc/")
        get_length_of_files = len(os.listdir(get_media_path))
        if get_length_of_files >= 1:
            shutil.rmtree(get_media_path)
    return os.path.join(get_aggreement_type_instance,str(get_owner_instance.get_groups),string_formatter,"aggreement_valid_doc",filename)


def upload_to_rental_user_ghar_patti_doc(instance,filename):
    get_rental_user_instance = get_object_or_404(AccountRental,id=instance.user.id)
    get_owner_instance = get_object_or_404(UserAndInvestor , id = instance.owner.id)
    print(get_owner_instance.__dir__())
    # get_contract_instance = get_object_or_404(Rental,id = instance.id)
    string_formatter = f"{get_owner_instance.username} - {get_rental_user_instance.username} ({instance.uid})"
    get_aggreement_type_instance = f"{instance.agreement_type}"


    # check_directory_flag  = str(settings.BASE_DIR) + "/media" + "/Leave_and_License/" + string_formatter + "/ghar_patti_doc/"
    check_directory_flag  = os.path.join(str(settings.BASE_DIR) , "media" , "Leave_and_License" , string_formatter , "ghar_patti_doc/")
    if os.path.isdir(check_directory_flag):
        # get_media_path = os.path.join(settings.BASE_DIR,"media/" ,"Leave_and_License/" + string_formatter + "/" + "ghar_patti_doc/")
        get_media_path = os.path.join(settings.BASE_DIR,"media" ,"Leave_and_License" , string_formatter ,  "ghar_patti_doc/")

        get_length_of_files = len(os.listdir(get_media_path))
        if get_length_of_files >= 1:
            shutil.rmtree(get_media_path)
    return os.path.join(get_aggreement_type_instance,str(get_owner_instance.get_groups),string_formatter,"ghar_patti_doc",filename)

    
class Rental(Contract):
    # authentication_class = []
    gala = models.OneToOneField(Gala,on_delete=models.CASCADE,related_name="gala_rental_contract_detail",null=True)
    owner = models.ForeignKey(UserAndInvestor, on_delete=models.CASCADE,default=get_main_owner,related_name="get_investor_contract")
    user = models.ForeignKey(Rental, on_delete=models.CASCADE,related_name="rental_contract")
    agreement_type = models.CharField(max_length=255,default=AgreementType.Leave_and_License)
    agreement_valid_start_date = models.DateField(editable=True,default=datetime.date.today)
    agreement_valid_end_date = models.DateField(editable=True,blank=True,null=True)
    locking_period = models.DateField(editable=True,default=datetime.date.today)
    agreement_valid_doc = models.FileField(max_length = 255,upload_to=upload_to_rental_user_aggreement_valid_doc,validators=[FileExtensionValidator(['pdf'])], blank=True, null=True)
    ghar_patti_doc = models.FileField(max_length = 255 ,upload_to=upload_to_rental_user_ghar_patti_doc,validators=[FileExtensionValidator(['pdf'])],blank=True,null=True)
    ghar_patti_start_date = models.DateField(editable=True,default=datetime.date.today)
    ghar_patti_end_date = models.DateField(editable = True ,blank=True,null=True)

    # @property
    # def company_name(self):
    #     return self.gala.warehouse.company.name
    




    class Meta:
        verbose_name_plural = "Contract With Rental"

    def __str__(self):
        return "{}".format(self.agreement_type)
    
    def clean(self, *args, **kwargs):
        get_gala_instance = get_object_or_404(Gala,uid = self.gala.uid)
        check_group_name = self.owner.groups.first().name
        if check_group_name == "Owner" and get_gala_instance.is_allotted == True:
            raise ValidationError(
                "You have already allotted this gala to Investor"
                )
            return super(Rental, self).clean(*args, **kwargs)
        if check_group_name == "Owner" and get_gala_instance.is_allotted_to_farmer == True:
            get_farmer = Farmer.objects.get(warehouse__uid = self.gala.warehouse.uid)
            raise ValidationError(
                f"You have already allotted this gala to Farmer {get_farmer.user}"
                )
            return super(Rental, self).clean(*args, **kwargs)

        if check_group_name == "Investor":
            try:
                get_investor_instance = Investor.objects.get(gala=self.gala)
                if get_investor_instance.user != self.owner:
                    get_farmer = Farmer.objects.get(warehouse__uid = self.gala.warehouse.uid)
                    raise ValidationError(
                         f"This gala is  belong to farmer {get_farmer.user}"
                        )
                    # raise ValidationError(
                    #     f"you have not alloted this gala to {self.owner}"
                    #     )
                    return super(Rental, self).clean(*args, **kwargs)

            except Investor.DoesNotExist:
                raise ValidationError (
                    f"you have not alloted this gala to {self.owner}"
                )
                return super(Rental, self).clean(*args, **kwargs)
        
        if check_group_name == "Farmer":
            try:
                get_investor_instance = Gala.objects.get(uid=self.gala.uid)
                if get_investor_instance.is_allotted_to_farmer != True:
                    get_farmer = Farmer.objects.get(warehouse__uid = self.gala.warehouse.uid)
                    raise ValidationError(
                         f"This gala is  belong to farmer {get_farmer.user}"
                        )
                    return super(Rental, self).clean(*args, **kwargs)
            except Gala.DoesNotExist:
                raise ValidationError(
                         f"You have to allot this gala to farmer {self.owner}"
                        )
                return super(Rental, self).clean(*args, **kwargs)
            
            except Farmer.DoesNotExist:
                raise ValidationError(
                         f"You have to allot this gala to farmer {self.owner}"
                        )
            
        return super(Rental, self).clean(*args, **kwargs)
    
    @property
    def get_differ_days(self):
        get_days = datetime.datetime.today().date() - self.agreement_valid_end_date
        return get_days.days


    
    def save(self, *args, **kwargs):
        self.clean()
        get_gala_instance = get_object_or_404(Gala,uid = self.gala.uid)
        get_gala_instance.is_allotted_to_rental = True
        get_gala_instance.save()
        super(Rental, self).save(*args, **kwargs)
    

    def delete(self, *args, **kwargs):
        get_gala_instance = get_object_or_404(Gala,uid = self.gala.uid)
        get_gala_instance.is_allotted_to_rental = False
        get_gala_instance.save()
        super(Rental, self).delete()


def upload_to_rental_user_history_aggreement_valid_doc(instance,filename):
    get_rental_user_instance = get_object_or_404(AccountRental,id=instance.renew_user.id)
    get_owner_instance = get_object_or_404(UserAndInvestor , id = instance.renew_owner.id)
    string_formatter = f"{get_owner_instance.username} - {get_rental_user_instance.username} ({instance.uid})"
    get_aggreement_type_instance = f"{instance.agreement_type}"


    check_directory_flag  = os.path.join(str(settings.BASE_DIR) , "media" , "Contract_History" , string_formatter , "aggreement_valid_doc/")
    if os.path.isdir(check_directory_flag):
        get_media_path = os.path.join(settings.BASE_DIR,"media" ,"Contract_History" , string_formatter , "aggreement_valid_doc/")
        get_length_of_files = len(os.listdir(get_media_path))
        if get_length_of_files >= 1:
            shutil.rmtree(get_media_path)
    return os.path.join(get_aggreement_type_instance,str(get_owner_instance.get_groups),string_formatter,"aggreement_valid_doc",filename)


def upload_to_rental_user_history_ghar_patti_doc(instance,filename):
    get_rental_user_instance = get_object_or_404(AccountRental,id=instance.renew_user.id)
    get_owner_instance = get_object_or_404(UserAndInvestor , id = instance.renew_owner.id)
    string_formatter = f"{get_owner_instance.username} - {get_rental_user_instance.username} ({instance.uid})"
    get_aggreement_type_instance = f"{instance.agreement_type}"

    check_directory_flag  = os.path.join(str(settings.BASE_DIR) , "media" , "Contract_History" , string_formatter , "ghar_patti_doc/")
    if os.path.isdir(check_directory_flag):
        get_media_path = os.path.join(settings.BASE_DIR,"media" ,"Contract_History" , string_formatter ,  "ghar_patti_doc/")

        get_length_of_files = len(os.listdir(get_media_path))
        if get_length_of_files >= 1:
            shutil.rmtree(get_media_path)
    return os.path.join(get_aggreement_type_instance,str(get_owner_instance.get_groups),string_formatter,"ghar_patti_doc",filename)



# class ContractHistory(Contract):
#     renew_gala = models.ForeignKey(Gala,on_delete=models.CASCADE,related_name="gala_contract_history",null=True)
#     renew_owner = models.ForeignKey(UserAndInvestor, on_delete=models.CASCADE,default=get_main_owner,related_name="owner_contract_history")
#     renew_user = models.ForeignKey(Rental, on_delete=models.CASCADE,related_name="user_contract_history")
#     renew_agreement_type = models.CharField(max_length=255,default=AgreementType.Leave_and_License)
#     renew_agreement_valid_start_date = models.DateField(editable=True,default=datetime.date.today)
#     renew_agreement_valid_end_date = models.DateField(editable=True,blank=True,null=True)
#     renew_agreement_valid_doc = models.FileField(max_length = 255,upload_to=upload_to_rental_user_history_aggreement_valid_doc ,validators=[FileExtensionValidator(['pdf'])], blank=True, null=True)
#     renew_ghar_patti_doc = models.FileField(max_length = 255 ,upload_to=upload_to_rental_user_history_ghar_patti_doc,validators=[FileExtensionValidator(['pdf'])],blank=True,null=True)
#     renew_ghar_patti_start_date = models.DateField(editable=True,default=datetime.date.today)
#     renew_ghar_patti_end_date = models.DateField(editable = True ,blank=True,null=True)
#     is_reNewed = models.BooleanField(default=False)
#     is_leaved = models.BooleanField(default=False)

#     class Meta:
#         verbose_name_plural = "Contract History"

#     def __str__(self):
#         return "Contract of ' {} ' Created with ' {} ' on  {} ".format(self.renew_owner.username,self.renew_user.username,self.renew_agreement_valid_start_date)



# def upload_to_rental_user_aggreement_valid_doc(instance,filename):
#     get_rental_user_instance = get_object_or_404(AccountRental,id=instance.renew_user.id)
#     get_owner_instance = get_object_or_404(UserAndInvestor , id = instance.renew_owner.id)
#     # get_contract_instance = get_object_or_404(Rental,id = instance.id)
#     string_formatter = f"{get_owner_instance.username} - {get_rental_user_instance.username} ({instance.uid})"
#     get_aggreement_type_instance = f"{instance.renew_agreement_type}"


#     # check_directory_flag  = str(settings.BASE_DIR) + "/media" + "/Leave_and_License/" + string_formatter + "/aggreement_valid_doc/"
#     check_directory_flag  = os.path.join(str(settings.BASE_DIR) , "media" , "Leave_and_License" , string_formatter , "aggreement_valid_doc/")
#     if os.path.isdir(check_directory_flag):
#         # get_media_path = os.path.join(settings.BASE_DIR,"media/" ,"Leave_and_License/" + string_formatter + "/" + "aggreement_valid_doc/")
#         get_media_path = os.path.join(settings.BASE_DIR,"media" ,"Leave_and_License" , string_formatter , "aggreement_valid_doc/")
#         get_length_of_files = len(os.listdir(get_media_path))
#         if get_length_of_files >= 1:
#             shutil.rmtree(get_media_path)
#     return os.path.join(get_aggreement_type_instance,string_formatter,"aggreement_valid_doc",filename)


# def upload_to_rental_user_ghar_patti_doc(instance,filename):
#     get_rental_user_instance = get_object_or_404(AccountRental,id=instance.renew_user.id)
#     get_owner_instance = get_object_or_404(UserAndInvestor , id = instance.renew_owner.id)
#     # get_contract_instance = get_object_or_404(Rental,id = instance.id)
#     string_formatter = f"{get_owner_instance.username} - {get_rental_user_instance.username} ({instance.uid})"
#     get_aggreement_type_instance = f"{instance.renew_agreement_type}"


#     # check_directory_flag  = str(settings.BASE_DIR) + "/media" + "/Leave_and_License/" + string_formatter + "/ghar_patti_doc/"
#     check_directory_flag  = os.path.join(str(settings.BASE_DIR) , "media" , "Leave_and_License" , string_formatter , "ghar_patti_doc/")
#     if os.path.isdir(check_directory_flag):
#         # get_media_path = os.path.join(settings.BASE_DIR,"media/" ,"Leave_and_License/" + string_formatter + "/" + "ghar_patti_doc/")
#         get_media_path = os.path.join(settings.BASE_DIR,"media" ,"Leave_and_License" , string_formatter ,  "ghar_patti_doc/")

#         get_length_of_files = len(os.listdir(get_media_path))
#         if get_length_of_files >= 1:
#             shutil.rmtree(get_media_path)
#     return os.path.join(get_aggreement_type_instance,string_formatter,"ghar_patti_doc",filename)

