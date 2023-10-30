import uuid, random, urllib
from rest_framework import serializers
from django.contrib.auth.models import Group
from contract.models import (
    Contract,
    Investor as ContractInvestor,
    Rental as ContractRental,
    Farmer as ContractFarmer
)
from warehouse.models import (
    Company,
    Property,
    Gala
)
from django.urls import reverse

from django.shortcuts import get_object_or_404
from account.models import (
    Investor,
    User,
    Rental,
    Owner,
    UserAndInvestor,
    Farmer
)
from datetime import datetime

# from service.service_api.serializers import (
#     SubServiceSerializer
# )
from service.models import (
    SubService
)

from django.template.defaultfilters import slugify
from django.forms.models import model_to_dict
from django.core.exceptions import ValidationError
from django.db.models import (
    Prefetch
)

"""    Common Function  """

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('name',)

    def to_representation(self, obj):
        return obj.name

class UserInvestorSerializer(serializers.ModelSerializer):
    # groups = serializers.CharField()
    # groups = GroupSerializer(many=True)
    # groups = serializers.SlugRelatedField(
    #     many=True,
    #     read_only=True,
    #     slug_field='name',
    # ) 
    class Meta:
        model = Investor
        fields = ['user_uid','username','first_name','last_name','email','phone','address','city']


class UserRentalSerializer(serializers.ModelSerializer):
    # groups = serializers.SlugRelatedField(
    #     many=True,
    #     read_only=True,
    #     slug_field='name',
    # ) 
    # groups = serializers.CharField()
    # groups = serializers.StringRelatedField(source="groups.first.name")
    # groups = GroupSerializer(many=True)
    class Meta:
        model = Rental
        fields = ['user_uid','username','first_name','last_name','email','phone','address','city']
    
    # def get_groups(self, obj):
    #     return [group.name for group in obj.groups]


class UserSerializer(serializers.ModelSerializer):
    # groups = serializers.SlugRelatedField(
    #     many=True,
    #     read_only=True,
    #     slug_field='name',
    #  )
    # groups = serializers.CharField()
    # groups = serializers.CharField()
    # groups = GroupSerializer(many=True)
    # get_group_name = serializers.CharField()
    class Meta:
        model = User
        fields = ['user_uid','username','email','phone','address','city']
        # depth = 1
    
    # def get_groups(self, obj):
    #     return [group.name for group in obj.groups]


def build_url(*args, **kwargs):
    get = kwargs.pop('get', {})
    url = reverse(*args, **kwargs)
    if get:
        url += '?' + urllib.parse.urlencode(get)
    return url

"""    Common Function  """

# class ContractSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Contract
#         fields = ['agreement_type']

class CompanySerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    class Meta:
        model = Company
        fields = ['id','uid','name','url']
    
    def get_url(self,instance):
        return instance.get_tenant_url()
        
class PropertySerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    total_number_of_galas = serializers.IntegerField()
    total_number_of_investors = serializers.IntegerField()
    class Meta:
        model = Property
        fields = ['uid','property_name','property_type','property_survey_number','address','city','state','country','total_number_of_galas','total_number_of_investors','url']

    def get_url(self,instance):
        get_company_type = self.context.get("company_type")
        url = build_url('get-investors-gala-detail', get={'company_type': get_company_type},kwargs={"uuid":instance['uid']})
        return url
    
    def to_representation(self,instance):
        data = super(PropertySerializer,self).to_representation(instance)

        if data['total_number_of_galas'] == None:
            data['total_number_of_galas'] = 0
        
        if data['total_number_of_investors'] == None:
            data['total_number_of_investors'] = 0 

        return data
        
class OwnerPropertySerializer(serializers.ModelSerializer):
    investor_contract_url = serializers.SerializerMethodField()
    rental_contract_url = serializers.SerializerMethodField()
    remaining_gala_url = serializers.SerializerMethodField()
    total_number_of_galas = serializers.IntegerField()
    total_number_of_investors = serializers.IntegerField()
    total_number_of_rentals = serializers.IntegerField()
    total_number_of_remaining_galas = serializers.IntegerField()
    class Meta:
        model = Property
        fields = ['uid','property_name','property_type','property_survey_number','address','city','state','country',
        'total_number_of_galas','total_number_of_investors','total_number_of_rentals',
        'total_number_of_remaining_galas','investor_contract_url','rental_contract_url','remaining_gala_url']

    def get_investor_contract_url(self,instance):
        get_company_type = self.context.get("company_type")
        url = build_url('get-owner-investor-contract-detail', get={'company_type': get_company_type},kwargs={"uuid":instance['uid']})
        return url

    def get_rental_contract_url(self,instance):
        get_company_type = self.context.get("company_type")
        url = build_url('get-owner-rental-contract-detail', get={'company_type': get_company_type},kwargs={"uuid":instance['uid']})
        return url
    
    def to_representation(self,instance):
        data = super(OwnerPropertySerializer,self).to_representation(instance)
        data['investor_user_type'] = "get-owner-investor-contract-detail"
        data['rental_user_type'] = "get-owner-rental-contract-detail"

        if data['total_number_of_galas'] is None:
            data['total_number_of_galas'] = 0
        
        if data['total_number_of_investors'] is None:
            data['total_number_of_investors'] = 0 

        if data['total_number_of_rentals'] is None:
            data['total_number_of_rentals'] = 0

        if data['total_number_of_remaining_galas'] is None:
            data['total_number_of_remaining_galas'] = 0
        return data

    def get_remaining_gala_url(self,instance):
        get_company_type = self.context.get("company_type")
        url = build_url('get-owner-remaining-gala-detail', get={'company_type': get_company_type},kwargs={"uuid":instance['uid']})
        return url


class FarmerPropertySerializer(serializers.ModelSerializer):
    total_remaining_galas = serializers.IntegerField()
    farmer_uid = serializers.CharField()
    url = serializers.SerializerMethodField()
    remaining_gala_url = serializers.SerializerMethodField()
    farmer_name = serializers.CharField()
    total_number_of_galas = serializers.IntegerField()
    total_gala_allotted = serializers.IntegerField()
    total_number_of_rentals = serializers.IntegerField()
    # total_number_of_investors = serializers.IntegerField()
    class Meta:
        model = Property
        fields = ['uid','property_name','property_type','property_survey_number','address','city','state','country','total_number_of_galas','total_gala_allotted','total_number_of_rentals','total_remaining_galas','farmer_name','farmer_uid','url','remaining_gala_url']
    
    def get_url(self,instance):
        get_company_type = self.context.get("company_type")
        url = build_url('get-farmers-gala-detail', get={'company_type': get_company_type},kwargs={"uuid":instance['farmer_uid'],"warehouse_uid" :instance['uid']})
        return url

    def get_remaining_gala_url(self,instance):
        get_company_type = self.context.get("company_type")
        url = build_url('get-farmer-remaining-galas-detail',get={"company_type":get_company_type},kwargs={"uuid":instance['uid']})
        return url
    
    def to_representation(self, instance):
        data = super(FarmerPropertySerializer, self).to_representation(instance)
        if data['total_number_of_galas'] is None:
            data['total_number_of_galas'] = 0
        if data['total_number_of_rentals'] is None:
            data['total_number_of_rentals'] = 0
        if data['total_gala_allotted'] is None:
            data['total_gala_allotted'] = 0
        if data['total_remaining_galas'] is None:
            data['total_remaining_galas'] = 0   
        return data
    

class ContractInvestorSerializer(serializers.ModelSerializer):
    owner = UserSerializer()
    user = UserInvestorSerializer()
    class Meta:
        model = ContractInvestor
        # fields = "__all__"
        exclude = ['polymorphic_ctype','gala','id','created_at','updated_at']

    def to_representation(self,instance):
        data = super(ContractInvestorSerializer,self).to_representation(instance)
        # if data['agreement_valid_start_date'] is not None:
        #     data['agreement_valid_start_date'] = datetime.strptime(data['agreement_valid_start_date'],"%Y-%m-%d").strftime("%d %b, %Y")

        # if data['agreement_valid_end_date'] is not None:
        #     data['agreement_valid_end_date'] = datetime.strptime(data['agreement_valid_end_date'],"%Y-%m-%d").strftime("%d %b, %Y")

        return data


class ContractRentalSerializer(serializers.ModelSerializer):
    owner = UserSerializer()
    user = UserRentalSerializer()
    class Meta:
        model = ContractRental
        fields = ['owner','user','uid','agreement_type','agreement_valid_doc','ghar_patti_doc','agreement_valid_start_date','agreement_valid_end_date','created_at','updated_at']

    def to_representation(self,instance):
        data = super(ContractRentalSerializer,self).to_representation(instance)
        # if data['agreement_valid_start_date'] is not None:
        #     data['agreement_valid_start_date'] = datetime.strptime(data['agreement_valid_start_date'],"%Y-%m-%d").strftime("%d %b, %Y")

        # if data['agreement_valid_end_date'] is not None:
        #     data['agreement_valid_end_date'] = datetime.strptime(data['agreement_valid_end_date'],"%Y-%m-%d").strftime("%d %b, %Y")

        return data
    
        
class GalaSerializer(serializers.ModelSerializer):
    gala_investor_contract_detail = ContractInvestorSerializer()
    gala_rental_contract_detail = ContractRentalSerializer()
    class Meta:
        model = Gala
        fields = ['uid','gala_number','is_allotted','is_allotted_to_rental','gala_investor_contract_detail','gala_rental_contract_detail']
        # depth = True
    
    def to_representation(self, instance):
        data = super(GalaSerializer, self).to_representation(instance)
        # if data['get_gala_detail'] is None:
        #     data['get_gala_detail'] = {}
        get_company_type = self.context.get("company_type")
        data['gala_rental_detail_url'] = build_url("get-investor-rental-gala-detail-view",get={"company_type":get_company_type},kwargs = {"uuid":data['uid']})
        return data

class FarmerGalaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gala
        fields = ['uid','gala_number','is_allotted']




class OwnerInvestorGalaSerializer(serializers.ModelSerializer):
    gala_investor_contract_detail = ContractInvestorSerializer()
    class Meta:
        model = Gala
        fields = ['uid','gala_number','is_allotted','is_allotted_to_rental','gala_investor_contract_detail']
    
    # def to_representation(self, instance):
    #     data = super(OwnerInvestorGalaSerializer, self).to_representation(instance)
    #     # if data['get_owner_investor_gala_detail'] is None:
    #     data['']

class OwnerRentalGalaSerializer(serializers.ModelSerializer):
    gala_rental_contract_detail = ContractRentalSerializer()
    class Meta:
        model = Gala
        fields = ['uid','gala_number','is_allotted','gala_rental_contract_detail']


class PropertyDetailSerializer(serializers.ModelSerializer):
   
    # company = CompanySerializer()
    property_leave_and_license_url = serializers.SerializerMethodField()
    total_number_of_galas = serializers.IntegerField()
    number_of_galas_is_allotted = serializers.IntegerField()
    remaining_number_of_galas = serializers.IntegerField()
    class Meta:
        model = Property
        fields = ['uid','property_name','total_number_of_galas','number_of_galas_is_allotted','remaining_number_of_galas','property_leave_and_license_url']
    
    def to_representation(self,instance):
        data = super(PropertyDetailSerializer,self).to_representation(instance)
        if data['number_of_galas_is_allotted'] is None:
            data['number_of_galas_is_allotted'] = 0
        if data['remaining_number_of_galas'] is None:
            data['remaining_number_of_galas'] = 0
        return data
    
    def get_property_leave_and_license_url(self,instance):
        get_property_instance = get_object_or_404(Property,uid = instance['uid'])
        return get_property_instance.get_absolute_url()


class OwnerRemainingGalaDetailSerializer(serializers.ModelSerializer):
    warehouse = serializers.StringRelatedField()
    class Meta:
        model = Gala
        fields = ['uid','warehouse','gala_number','is_allotted','is_allotted_to_farmer','is_allotted_to_rental','gala_area_size','gala_price']
    
class OwnerTotalRemainingGalaCountSerializer(serializers.ModelSerializer):
    # total_remaining_gala_count = serializers.IntegerField()

    class Meta:
        model = Property 
        exclude = ['updated_at']

    # def to_representation(self, instance):
    #     print(instance)
    #     data = super(OwnerTotalRemainingGalaCountSerializer,self).to_representation(instance)
    #     return data


class RentalContractGalaDetail(serializers.ModelSerializer):
    owner = UserSerializer()
    class Meta:
        model = ContractRental
        fields = ['owner']
    

class RentalGalaSerializer(serializers.ModelSerializer):
    gala_rental_contract_detail = RentalContractGalaDetail()
    # number_of_rentals = serializers.CharField()
    # gala_investor_contract_detail = ContractInvestorSerializer()
    class Meta:
        model = Gala
        fields = ['gala_rental_contract_detail','uid']



class LiveAndLicenseWarehouseSerializer(serializers.ModelSerializer):
    owner_type = serializers.CharField()
    detail_url = serializers.SerializerMethodField()
    total_gala_count = serializers.IntegerField()
    total_allotted_galas = serializers.IntegerField()
    total_remaining_galas = serializers.IntegerField()
    class Meta:
        model = Property
        fields = ['uid','property_name','city','is_allotted_to_farmer','owner_type','total_gala_count','total_allotted_galas','total_remaining_galas','detail_url']

    def to_representation(self, instance):
        data = super(LiveAndLicenseWarehouseSerializer,self).to_representation(instance)
        if data['total_allotted_galas'] == None:
            print(data['total_allotted_galas'])
            data['total_allotted_galas'] = 0
        
        if data['total_remaining_galas'] == None:
            data['total_remaining_galas'] = 0
        
        if data['total_gala_count'] == None:
            data['total_gala_count'] = 0
        
        if data['is_allotted_to_farmer'] == False:
            data['owner_type'] = f"{data['owner_type']} (Developer)"
        
        if data['is_allotted_to_farmer'] == True:
            data['owner_type'] = f"{data['owner_type']} (Farmer)"
        data['property_slug'] = slugify(data['property_name'])
        return data

    def get_detail_url(self,instance):
        get_company_type = self.context.get("company_type")
        url = build_url("get-live-and-license-detail-api",get={"company_type":get_company_type},kwargs={"uuid":instance['uid']})
        return url

class LiveAndLicensePropertySerializer(serializers.ModelSerializer):
    company = serializers.StringRelatedField()
    class Meta:
        model = Property
        exclude = ['created_at','updated_at']

class LeaveAndLicenseOwnerSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True)
    class Meta:
        model = Owner
        fields = ['user_uid','username','email','phone','address','city','groups']


class LeaveAndLicenseInvestorSerializer(serializers.ModelSerializer):
    # groups = GroupSerializer(many=True)
    class Meta:
        model = Investor
        fields = ['user_uid','username','email','phone','address','city']


class LeaveAndLicenseUserAndInvestorSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True)
    class Meta:
        model = UserAndInvestor
        fields = ['user_uid','username','email','phone','address','city','groups']


class LeaveAndLicenseRentalSerializer(serializers.ModelSerializer):
    # groups = GroupSerializer(many=True)
    class Meta:
        model = Rental
        fields = ['user_uid','username','email','phone','address','city']



class LiveAndLicenseContractInvestorSerializer(serializers.ModelSerializer):
    # polymorphic_ctype = serializers.StringRelatedField()
    user = LeaveAndLicenseInvestorSerializer()
    owner = LeaveAndLicenseOwnerSerializer()
    # groups = GroupSerializer()
    # user = serializers.CharField(source = "user.username")

    class Meta:
        model = ContractInvestor
        fields = ['owner','user']
        # fields = ['user','polymorphic_ctype']
    
    # def get_user_type(self,instance) -> None:
    #     print(instance.__dir__())

    
    # def to_representation(self, instance):
    #     data = super(LiveAndLicenseContractInvestorSerializer,self).to_representation(instance)
    #     data['testing'] = data
    #     return data

class LiveAndLicenseContractRentalSerializer(serializers.ModelSerializer):
    owner = LeaveAndLicenseUserAndInvestorSerializer()
    user = LeaveAndLicenseRentalSerializer()
    # user = LeaveAndLicenseUserInvestorSerializer()
    # owner = LeaveAndLicenseUserInvestorSerializer()
    # owner = UserSerializer()
    # user = UserRentalSerializer()
    # user = serializers.CharField(source="user.username")
   
    class Meta:
        model = ContractRental
        fields = ['owner','user']
        # fields = ['user','gala']

class LiveAndLicenseDetailSerializer(serializers.ModelSerializer):
    # get_owner_type = serializers.CharField()
    # gala_rental_contract_detail__owner__groups = serializers.CharField()
    # gala_investor_contract_detail = LiveAndLicenseContractInvestorSerializer(many=True)
    # gala_rental_contract_detail = LiveAndLicenseContractRentalSerializer(many=True)
    gala_investor_contract_detail = LiveAndLicenseContractInvestorSerializer()
    gala_rental_contract_detail = LiveAndLicenseContractRentalSerializer()

    class Meta:
        model = Gala
        fields = ['uid','gala_number','gala_area_size','gala_price','is_allotted','is_allotted_to_rental','is_allotted_to_farmer','gala_rental_contract_detail','gala_investor_contract_detail']
        # depth = 1
    
    def to_representation(self, instance):
        data = super(LiveAndLicenseDetailSerializer,self).to_representation(instance)
        
        if data['gala_rental_contract_detail'] != None:
            data["gala_rental_contract_detail"]['user']['groups'] = "Rental"
            data["gala_rental_contract_detail"]['owner']['groups'] = data.get("gala_rental_contract_detail")["owner"].get("groups","N/A")[0]
        if data['gala_investor_contract_detail'] != None:
            data["gala_investor_contract_detail"]['user']['groups'] = "Investor"
            data["gala_investor_contract_detail"]['owner']["groups"] = data.get("gala_investor_contract_detail")["owner"].get("groups","N/A")[0]
        # if data['gala_investor_contract_detail'] is None:
        #     print(data['gala_investor_contract_detail'].__dir__())
        #     data['gala_investor_contract_detail'] = "Developer"
        return data
        
    
    # def to_representation(self, instance):
    #     data = super(LiveAndLicenseDetailSerializer,self).to_representation(instance)
    #     return data



# class TestGalaSerializer(serializers.ModelSerializer):
#     gala_rental_contract_detail = LiveAndLicenseContractRentalSerializer()
#     gala_investor_contract_detail = LiveAndLicenseContractInvestorSerializer()
#     class Meta:
#         model = Gala
#         fields = ['uid','gala_number','is_allotted','is_allotted_to_rental','gala_investor_contract_detail','gala_rental_contract_detail']
#         # fields =['uid','gala_number','is_allotted','','gala_investor_contract_detail']


class LiveAndLicensePropertyGalaSerializer(serializers.ModelSerializer):
    # get_gala = TestGalaSerializer(many=True)
    # get_owner_type = serializers.CharField()
    class Meta:
        model = Property
        # fields = "__all__"
        exclude = ['id','created_at',"updated_at","company"]
    
    def to_representation(self,instance):
        data = super(LiveAndLicensePropertyGalaSerializer,self).to_representation(instance)
        gala_instance = instance.get_gala.select_related(
            "gala_rental_contract_detail__owner",
            "gala_rental_contract_detail__user",
            "gala_investor_contract_detail__owner",
            # "gala_investor_contract_detail__polymorphic_ctype",
            'gala_investor_contract_detail__user',
        ).prefetch_related(
                "gala_rental_contract_detail__owner__groups",
                # "gala_rental_contract_detail__user__groups",
                "gala_investor_contract_detail__owner__groups",
                # "gala_investor_contract_detail__user__groups",
            )
        
        # Staff.objects.all().prefetch_related(Prefetch('courses', queryset=Course.objects.only('name').all()))
        
        data['get_gala'] = LiveAndLicenseDetailSerializer(gala_instance,many=True).data
        # gala_investor_contract_instance = instance.get_gala.select_related("gala_investor_contract_detail__owner","gala_investor_contract_detail__user")
        # data['']
        return data


# jan 
class ContractRentalGalaSerializer(serializers.ModelSerializer):
    gala_number = serializers.CharField(source="gala.gala_number")
    gala_uid = serializers.CharField(source="gala.uid")
    class Meta:
        model = ContractRental
        fields = ['gala',"gala_uid","gala_number"]
    
    # def to_representation(self, instance):
    #     data = super(ContractRentalGalaSerializer,self).to_representation(instance)
    #     print(self.context)
    #     data['sub-service'] = SubServiceSerializer(SubService.objects.filter(service__service_name__icontains=self.context.get("service_type")),many=True).data
    #     return 

#POST API

class CompanyPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"

class PropertyPostSerializer(serializers.ModelSerializer):
    company = serializers.CharField()
    class Meta:
        model = Property
        fields = ['uid','company','property_name','address','city','zipcode','country','state','property_type','property_survey_number']
        extra_kwargs = {
            'property_survey_number':{"required":True},
            'uid':{"read_only":True}
            }
    

    def validate(self, attrs):
        try:
            attrs['company'] = Company.objects.get(uid=attrs['company'])
            return attrs
        except Company.DoesNotExist:
            raise ValidationError("Company not found")
        
    def create(self, validated_data):
        try:
            property_instance = Property.objects.create(
                company = validated_data['company'],
                property_name = validated_data['property_name'],
                address = validated_data['address'],
                city = validated_data['city'],
                zipcode = validated_data['zipcode'],
                country = validated_data['country'],
                state = validated_data['state'],
                property_type = validated_data['property_type'],
                property_survey_number = validated_data['property_survey_number']
            )      
            return property_instance
        except Exception as e:
            raise serializers.ValidationError({
                "errors":str(e)
            })
    
    # def to_representation(self, instance):
    #     response = super().to_representation(instance)
    #     # print(instance)
    #     # response['company'] = CompanyPostSerializer(instance.company).data
    #     # print(response)
    #     return response
    


    # def to_representation(self, instance):
    #     data = super(PropertyPostSerializer,self).to_representation(instance)
    #     print(data)
    #     for field, value in data.items():
    #         if value is None:
    #             raise ValidationError({field: "can't be None"})
    #     return data

class PropertyListSerializer(serializers.ModelSerializer):

    company = serializers.StringRelatedField()
    total_gala = serializers.IntegerField()
    gala_url = serializers.SerializerMethodField()
    class Meta:
        model = Property
        # fields = "__all__"
        exclude = ['created_at', 'updated_at']
        # fields = [
        #     'id','uid','company',
        #     'property_name','property_type',
        #     'property_survey_number','address',
        #     'city','zipcode','country','state',
        #     'is_allotted_to_farmer',
        #     'total_gala']

    def get_gala_url(self,instance):
        get_company_type = self.context.get("company_type")
        url = build_url("get-gala-with-property-uid",get={"company_type":get_company_type},kwargs={"property_uid":instance.uid})
        return url
    

class GalaPostSerializer(serializers.ModelSerializer):
    warehouse = serializers.CharField()
    class Meta:
        model = Gala
        fields = ['warehouse','gala_area_size', 'gala_price','gala_number']

    def validate(self, attrs):
        try:
            attrs['warehouse'] = Property.objects.get(uid=attrs['warehouse'])
            return attrs
        except Property.DoesNotExist:
            raise ValidationError({"warehouse":("Property not found")})
        
    def create(self, validated_data):
        try:
            gala_instance = Gala.objects.create(
                warehouse = validated_data['warehouse'],
                gala_area_size = validated_data['gala_area_size'],
                gala_price = validated_data['gala_price'],
                gala_number = validated_data['gala_number']
            )      
            return gala_instance
        except Exception as e:
            raise serializers.ValidationError({
                "errors":str(e)
            })
    

class OwnerPropertyListSerializer(serializers.ModelSerializer):
    warehouse_gala = serializers.SerializerMethodField()
    class Meta:
        model = Property
        fields = ['uid','property_name','warehouse_gala']

    def get_warehouse_gala(self,instance):
        get_company_type = self.context.get("company_type")
        url = build_url("get-owner-warehouse-galas",get={"company_type":get_company_type},kwargs={"uuid":instance.uid})
        return url


class OwnerPropertyGalaListSerializer(serializers.ModelSerializer):
    warehouse = serializers.StringRelatedField()
    class Meta:
        model = Gala
        fields = ['warehouse','uid','gala_number']


class PropertyGalaSerializer(serializers.ModelSerializer):
    # warehouse = serializers.StringRelatedField()
    class Meta:
        model = Gala
        fields = ['id','uid','gala_number','gala_area_size','gala_price','is_allotted','is_allotted_to_rental','is_allotted_to_farmer','warehouse']
        # fields = "__all__"



class GalaUpdateSerializer(serializers.ModelSerializer):
    warehouse = serializers.CharField()
    gala_area_size = serializers.FloatField(required=True)
    gala_price = serializers.FloatField(required=True)
    class Meta:
        model = Gala
        fields = ['warehouse','gala_area_size','gala_price']

        # extra_kwargs = {
        #     "gala":{"read_only":True}
        # }

    def validate(self, attrs):
        try:
            attrs['warehouse'] = Property.objects.get(uid = attrs['warehouse']).id
            return attrs
        except Exception as exception:
            return str(exception)
# had to add gala_number in the update method 
        
    def update(self, instance, validated_data):
        try:
            instance = Gala.objects.get(
                uid = instance.uid
            )
            instance.warehouse_id = validated_data['warehouse']
            instance.gala_area_size = validated_data['gala_area_size']
            instance.gala_price = validated_data['gala_price']
            instance.save()


        except Exception as exception:
            return str(exception)
        return instance

class RentalCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Company
        fields =['name']

class RentalPropertySerializer(serializers.ModelSerializer):
    company = RentalCompanySerializer()

    class Meta:
        model = Property
        fields = ['uid','company','property_name','property_type','property_survey_number','address','city','state','country']

class RentalPropertyGalaSerializer(serializers.ModelSerializer):
    # gala_rental_contract_detail = ContractRentalSerializer()
    warehouse = RentalPropertySerializer()
    class Meta:
        model = Gala
        fields = ['gala_number','warehouse']


class FarmerRemainingGalaDetailSerializer(serializers.ModelSerializer):
    warehouse = serializers.StringRelatedField()
    class Meta:
        model = Gala
        # fields = "__all__"
        exclude = ['created_at','updated_at','id']
#for farmer and rental detail view
class FarmerCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Company
        fields =['name']

class FarmerPropertyGalaSerializer(serializers.ModelSerializer):
    company = FarmerCompanySerializer()

    class Meta:
        model = Property
        fields = ['uid','property_name','property_type','property_survey_number','address','city','state','country']


class FarmerGalaDetailSerializer(serializers.ModelSerializer):
    warehouse = FarmerPropertyGalaSerializer()
    class Meta:
        model = Gala
        fields = ['gala_number','warehouse']



class InvestorCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Company
        fields =['name']

class InvestorPropertySerializer(serializers.ModelSerializer):
    company = InvestorCompanySerializer()

    class Meta:
        model = Property
        fields = ['uid','company','property_name','property_type','property_survey_number','address','city','state','country']

class InvestorPropertyGalaSerializer(serializers.ModelSerializer):
    # gala_rental_contract_detail = ContractRentalSerializer()
    warehouse = InvestorPropertySerializer()
    class Meta:
        model = Gala
        fields = ['uid','gala_number','warehouse']


class ViewContractGalaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gala
        fields = ['gala_number','gala_area_size','gala_price']


class DashboardViewSerializer(serializers.ModelSerializer):
    total_warehouse_count = serializers.IntegerField()
    total_gala_count = serializers.IntegerField()
    total_rental_count = serializers.IntegerField()
    total_investor_count = serializers.IntegerField()
    total_farmer_count = serializers.IntegerField()
    total_remaining_gala_count = serializers.IntegerField()

    class Meta:
        model = Company
        fields = [
            'uid','name','total_warehouse_count','total_gala_count',
            'total_rental_count','total_investor_count','total_farmer_count',
            'total_remaining_gala_count'
        ]


 

class OwnerWarehouseListForFarmerSerializer(serializers.ModelSerializer):
    total_galas = serializers.CharField()
    total_number_of_galas = serializers.CharField()
    # warehouse_gala = serializers.SerializerMethodField()
    class Meta:
        model = Property
        fields = ['uid',"property_name","total_galas","total_number_of_galas"]
    
    # def get_warehouse_gala(self,instance):
    #     get_company_type = self.context.get("company_type")
    #     url = build_url("get-owner-warehouse-galas",get={"company_type":get_company_type},kwargs={"uuid":instance.uid})
    #     return url
    
    def to_representation(self,instance):
        get_company_type = self.context.get("company_type")
        response = super(OwnerWarehouseListForFarmerSerializer,self).to_representation(instance)
        if response['total_galas'] == None:
            response['total_galas'] = 0
        response['warehouse_gala'] = build_url("get-owner-warehouse-galas",get={"company_type":get_company_type},kwargs={"uuid":response['uid']})
        return response

class ServiceRequestPropertySerializer(serializers.ModelSerializer):
    company = serializers.CharField()
    class Meta:
        model = Property
        fields = ['uid','company','property_name','address','city','zipcode','country','state','property_type','property_survey_number']
    

class ServiceRequestGalaSerializer(serializers.ModelSerializer):
    warehouse  = ServiceRequestPropertySerializer()
    class Meta:
        model = Gala
        fields = ['warehouse','gala_number','gala_area_size','gala_price']



class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ['property_name','address','property_survey_number']

class InvestorGalaSerializer(serializers.ModelSerializer):
    warehouse = WarehouseSerializer()

    class Meta:
        model = Gala
        fields = ['uid','warehouse','gala_number','is_allotted','is_allotted_to_rental','gala_area_size','gala_price']

class InvestorRemainingGalaSerializer(serializers.ModelSerializer):
    gala = InvestorGalaSerializer()
    class Meta:
        model = ContractInvestor
        # fields = ['uid','is_allotted','is_allotted_to_farmer','is_allotted_to_rental','gala_area_size','gala_price']
        fields = ['gala']

class InvestorRentalDetailSerializer(serializers.ModelSerializer):
    owner = UserInvestorSerializer()
    user = UserRentalSerializer()
    gala = InvestorGalaSerializer()
    class Meta:
        model = ContractRental
        # fields = ['gala','owner','user','uid','']
        exclude = ['id','created_at','updated_at','polymorphic_ctype']




class UserOwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Owner
        fields = ['user_uid','username','email','phone','address','city']

class UserFarmerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farmer
        fields = ['user_uid','username','email','phone','address','city']

class FarmerWarehouseDetail(serializers.ModelSerializer):
    user = UserFarmerSerializer()
    class Meta:
        model = ContractFarmer
        fields = ['user']

class WarehouseDetailSerializer(serializers.ModelSerializer):
    farmer_warehouse_detail = FarmerWarehouseDetail()
    class Meta:
        model = Property
        fields = ['property_name','address','property_survey_number','farmer_warehouse_detail']

class GalaInvestorContractDetailSerializer(serializers.ModelSerializer):
    user = UserInvestorSerializer()
    class Meta:
        model = ContractInvestor
        fields = ['user']

class GalaRentalContractDetailSerializer(serializers.ModelSerializer):
    user = UserRentalSerializer()
    owner = UserOwnerSerializer()
    class Meta:
        model = ContractRental
        fields = ['user','owner']

class DashboardTotalGalaSerializer(serializers.ModelSerializer):
    warehouse = WarehouseDetailSerializer()
    gala_rental_contract_detail = GalaRentalContractDetailSerializer()
    gala_investor_contract_detail = GalaInvestorContractDetailSerializer()
    class Meta: 
        model = Gala
        fields = ['uid','gala_number','gala_area_size','gala_price','warehouse','gala_rental_contract_detail','gala_investor_contract_detail']
    
    def to_representation(self,instance):
        response = super(DashboardTotalGalaSerializer,self).to_representation(instance)
        if response['gala_rental_contract_detail']!= None and response['gala_investor_contract_detail'] == None and response['warehouse']['farmer_warehouse_detail'] == None:
            response['gala_rental_contract_detail']['owner']['username'] = "Developer"
        if response['gala_investor_contract_detail'] != None:
            response['gala_investor_contract_detail']['user']['username'] = response['gala_investor_contract_detail']['user']['username'] + " " + "(Investor)"
        if response['gala_rental_contract_detail'] != None:
            response['gala_rental_contract_detail']['user']['username'] = response['gala_rental_contract_detail']['user']['username'] + " " + "(Rental)"
            if response['gala_rental_contract_detail']['owner']['username'] != "Developer":
                response['gala_rental_contract_detail']['owner']['username'] = response['gala_rental_contract_detail']['owner']['username'] + " " + "(Investor)"
        if response['warehouse']['farmer_warehouse_detail'] != None:
            response['warehouse']['farmer_warehouse_detail']['user']['username'] =  response['warehouse']['farmer_warehouse_detail']['user']['username'] + " " + "(Investor)"
        return response


class FarmerDetailSerializer(serializers.ModelSerializer):
    # get_investor_contract = FarmerContractSerializer(many=True)
    class Meta:
        model = Farmer
        fields = ['user_uid','username','phone','address','city','zip_code','birth_date']

class ContractFarmerSerializerForDashboard(serializers.ModelSerializer):
    user = FarmerDetailSerializer()
    class Meta:
        model = ContractFarmer
        fields = ['user']

class WarehouseSerializerForDashboardView(serializers.ModelSerializer):
    farmer_warehouse_detail = ContractFarmerSerializerForDashboard()
    class Meta:
        model = Property
        fields = ['property_name','address','farmer_warehouse_detail']


class DashboardTotalRemainingGalaSerializer(serializers.ModelSerializer):
    warehouse = WarehouseSerializerForDashboardView()
    # farmer_warehouse_detail = ContractFarmerSerializerForDashboard(many=True)
    class Meta:
        model = Gala
        fields = ['uid','warehouse','gala_number','gala_price','gala_area_size']


class UpdatePropertySerializer(serializers.ModelSerializer):
    company = serializers.CharField()
    class Meta:
        model = Property
        fields = '__all__'
        # extra_kwargs  ={
        #     "company":{"required":False},
        # }
    
    def validate(self,attrs):
        try:
            attrs['company'] = Company.objects.get(uid = attrs['company']).id
            return attrs
        except Exception as exception:
            return str(exception)


    def update(self,instance,validated_data):
        try:
            print(instance,17)
            property_instance = Property.objects.get(
                uid = instance.uid
            )

            # property_instance.company_id = validated_data['company']
            property_instance.property_name = validated_data['property_name']
            property_instance.property_type = validated_data['property_type']
            # property_instance.property_survey_number = validated_data['property_survey_number']
            property_instance.address = validated_data['address']
            property_instance.city = validated_data['city']
            property_instance.zipcode = validated_data['zipcode']
            property_instance.country = validated_data['country']
            property_instance.state = validated_data['state']
            property_instance.save()
            return property_instance

            
        except Exception as exception:
            return str(exception)