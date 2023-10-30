from rest_framework import serializers
from service.models import Service,SubService,ServiceRequest,Image,LeaveGalaRequest,RenewGalaRequest
from warehouse.warehouse_api.serializers import (
    GalaSerializer,
    ViewContractGalaSerializer,
    ServiceRequestGalaSerializer,
    InvestorPropertyGalaSerializer
)
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta, timezone
from django import template
from django.utils.timesince import timesince
from django.urls import reverse
from contract.models import (
    Contract,
    Investor as ContractInvestor,
    Rental as ContractRental,

)
from account.account_api.serializers import (
    ViewContractRentalSerializer,
    ViewContractUserInvestorSerializer,
    ServiceRequestAccountRentalSerializer,
    DashboardAccountRentalListSerializer
)
from django.urls import reverse
from account.models import (
    Rental
)
from warehouse.models import (
    Property,
    Gala,
    Company,
)

from contract.contract_api.serializers import (
    InvestorRentalGalaDetailSerializer,
    RentalSerializer
)
from dateutil import parser





class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        # fields = '__all__'
        exclude = ['created_at', 'updated_at']


#iska matlab nai hai
class SubServiceSerializer(serializers.ModelSerializer):
    # service = ServiceSerializer()
    class Meta:
        model = SubService
        fields = ['service_uid','sub_service_name']
        # exclude = ['created_at', 'updated_at']
    
    # def to_representation(self,instance):
    #     data = super(SubServiceSerializer,self).to_representation(instance)
    #     # data['user_uid'] = self.context.get("user_uid")
    #     return data


class SubServicePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubService
        fields = "__all__"
        # depth = True
   
class ServicesRequestStatusSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source = "user.username")
    request_sub_service = serializers.CharField(source = "request_sub_service.sub_service_name")
    gala = serializers.CharField(source = "gala.uid")
    request_date = serializers.SerializerMethodField()
    request_time  = serializers.SerializerMethodField()

    class Meta:
        model = ServiceRequest
        fields = ['tracking_id','user','request_sub_service','gala','request_date','request_time','status','description']
    
    def get_request_date(self,instance):
        # print(instance.service_request_date.date)
        return instance.service_request_date.date()
    
    def get_request_time(self,instance):
        return instance.service_request_date.time()

# 04/02/2023
class SeriviceSerializerForServiceRequest(serializers.ModelSerializer):
    class Meta:
        model =  Service
        fields = ['service_name']


class ServiceRentalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rental
        fields = ['username','email','phone','address']

class SubServiceSerializer(serializers.ModelSerializer):
    
    service = SeriviceSerializerForServiceRequest()
    class Meta:
        model = SubService
        fields = ['service','sub_service_name']

class ServiceRequestGalaPropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ['property_name']

class ServiceRequestGalaSerializer(serializers.ModelSerializer):
    warehouse = ServiceRequestGalaPropertySerializer()
    class Meta:
        model = Gala
        fields = ['gala_number','warehouse']

class ServicesRequestSerializer(serializers.ModelSerializer):
    user = ServiceRentalSerializer()
    request_sub_service= SubServiceSerializer()
    gala = ServiceRequestGalaSerializer()
    class Meta:
        model = ServiceRequest
        fields = ['service_uid','tracking_id','service_request_date','user','request_sub_service','gala','status','created_at','updated_at','description']
        # depth = True

    def to_representation(self,instance):
        data = super(ServicesRequestSerializer,self).to_representation(instance)
        print(data['service_request_date'])
    #     print(data['service_request_date'],17)
        # if data['service_request_date'] is not None:
        #     # response = data['service_request_date'].split("T")[0]
        #     data['service_request_date'] = datetime.strptime(data['service_request_date'],"%Y-%m-%dT%H:%M:%S+05:30").strftime("%d %b, %Y")
        
            
        # if data['created_at'] is not None:
        #     # response = data['created_at'].split("T")[0]
        #     data['created_at'] = datetime.strptime(data['created_at'],"%Y-%m-%dT%H:%M:%S+05:30").strftime("%d %b, %Y")
            # data['created_at'] = datetime.strptime(response,"%Y-%m-%d").strftime("%d %b, %Y")

        # if data['updated_at'] is not None:
        #     response = data['updated_at'].split("T")[0]
        #     data['updated_at'] = datetime.strptime(response,"%Y-%m-%d").strftime("%d %b, %Y")

        # if data['created_at'] is not None:
        #     data['created_at'] = datetime.strptime(data['created_at'],"%Y-%m-%d").strftime("%d %b, %Y").split("T")[0]

        # if data['updated_at'] is not None:
        #     data['updated_at'] = datetime.strptime(data['updated_at'],"%Y-%m-%d").strftime("%d %b, %Y").split("T")[0]
        data['created_at'] = datetime.strptime(data['created_at'],"%Y-%m-%dT%H:%M:%S.%f+05:30").strftime("%d %b, %Y")
        data['updated_at'] = datetime.strptime(data['updated_at'],"%Y-%m-%dT%H:%M:%S.%f+05:30").strftime("%d %b, %Y")
        data['service_request_time'] = datetime.strptime(data['service_request_date'],"%Y-%m-%dT%H:%M:%S+05:30").strftime("%I:%M %p")
        data['service_request_date'] = datetime.strptime(data['service_request_date'],"%Y-%m-%dT%H:%M:%S+05:30").strftime("%d %b, %Y")
       

        return data

class RentalNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRequest
        fields =  ('get_status','get_date_time')


class ImageSerializer(serializers.ModelSerializer):
    # image = serializers.StringRelatedField()
    class Meta:
        model = Image
        fields = ['image']

class ServiceAllRequestSerializer(serializers.ModelSerializer):
    # service_request = serializers.StringRelatedField()
    # service_request = serializers.CharField(source="service_request.sub_service_name")
    # service_name = serializers.SerializerMethodField()
    request_sub_service = SubServiceSerializer()
    service_request_url=serializers.SerializerMethodField()
    class Meta:
        model = ServiceRequest
        include=['service_request_url']
        exclude = ['id','service_uid','created_at','updated_at','service_request_date','description','user','gala']

    # def get_service_name(self,instance):
    #     return instance.service_request.sub_service_name

    def get_service_request_url(self,instance):
        return reverse("get-rental-request-details",kwargs={"user_uid":self.context.get("user_uid"),"tracking_id":instance.tracking_id})
        # return instance.get_service_request_detail_url()


class LeaveGalaRequestSerializer(serializers.ModelSerializer):
    # company_name = serializers.CharField()
    user = DashboardAccountRentalListSerializer()
    gala = InvestorPropertyGalaSerializer()

    # gala_rental_contract_detail = InvestorRentalGalaDetailSerializer()
    class Meta:
        model = LeaveGalaRequest
        fields = ['uid','user','gala','reason_for_leaving','status','updated_at','created_at']
    
    def to_representation(self,instance):
        response = super(LeaveGalaRequestSerializer, self).to_representation(instance)
        datetime_obj  = parser.parse(response['updated_at']).replace(tzinfo=None)
        response['updated_at'] = datetime.strptime(str(datetime_obj),"%Y-%m-%d %H:%M:%S.%f").strftime("%d,%b %Y %I:%M %p")
        return response


        # # fields = '__all__'
        # exclude = ['id','created_at','updated_at','polymorphic_ctype']

class ViewContractSerializer(serializers.ModelSerializer):
    gala = ViewContractGalaSerializer()
    user = ViewContractRentalSerializer()
    owner = ViewContractUserInvestorSerializer()
    class Meta:
        model = ContractRental
        fields = [
            'uid','user','owner','gala','agreement_type',
            'agreement_valid_start_date','agreement_valid_end_date',
            'agreement_valid_doc','ghar_patti_start_date','ghar_patti_end_date',
            'ghar_patti_doc'
        ]

    def to_representation(self,instance):
        response = super(ViewContractSerializer, self).to_representation(instance)
        response['agreement_valid_start_date'] = datetime.strptime(response['agreement_valid_start_date'],"%Y-%m-%d").strftime("%d %b, %Y")
        response['agreement_valid_end_date'] = datetime.strptime(response['agreement_valid_end_date'],"%Y-%m-%d").strftime("%d %b, %Y")
        response['ghar_patti_start_date'] = datetime.strptime(response['ghar_patti_start_date'],"%Y-%m-%d").strftime("%d %b, %Y")
        response['ghar_patti_end_date'] = datetime.strptime(response['ghar_patti_end_date'],"%Y-%m-%d").strftime("%d %b, %Y")
        response['view_contract_url'] = reverse('view-contract-detail',kwargs= {"uuid" : response['uid']})
        return response


class ServiceRequestSerializer(serializers.ModelSerializer):
    user  = ServiceRequestAccountRentalSerializer()
    gala = ServiceRequestGalaSerializer()
    request_date = serializers.SerializerMethodField()
    service_request = serializers.CharField()
    service_request_images = ImageSerializer(many=True)
    class Meta:
        model = ServiceRequest
        fields = ['user','service_uid','tracking_id','status','request_date','description','service_request','gala','service_request_images']
    
    def get_request_date(self,instance):
        get_date = instance.service_request_date.date()
        return datetime.strptime(str(get_date), "%Y-%m-%d").strftime("%d-%m-%Y")

class CompanySerializerForRenewRequest(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['name']


class WarehouseSerializerForRenewGalaRequest(serializers.ModelSerializer):
    company = CompanySerializerForRenewRequest()
    class Meta:
        model = Property
        fields = ['property_name','company']

class GalaSerializerForRenewGalaRequest(serializers.ModelSerializer):
    warehouse = WarehouseSerializerForRenewGalaRequest()
    class Meta:
        model = Gala
        fields = ['uid','gala_number','warehouse']

class RenewGalaRequestSerializer(serializers.ModelSerializer):
    renew_user = RentalSerializer()
    renew_gala = GalaSerializerForRenewGalaRequest()
    uid = serializers.CharField()
    agreement_valid_doc = serializers.CharField()
    agreement_valid_start_date = serializers.CharField()
    agreement_valid_end_date = serializers.CharField()
    ghar_patti_doc = serializers.CharField()
    ghar_patti_start_date = serializers.CharField()
    ghar_patti_end_date = serializers.CharField()
    gala = serializers.CharField()
    owner = serializers.CharField()
    warehouse = serializers.CharField()
    rental = serializers.CharField()

    class Meta:
        model = RenewGalaRequest
        fields = [
            'renew_user','renew_gala','renew_uid','renew_status','renew_created_at','renew_updated_at',
            'uid','agreement_valid_doc','agreement_valid_start_date','agreement_valid_end_date','ghar_patti_doc',
            'ghar_patti_start_date','ghar_patti_end_date','gala','owner','warehouse','rental'
            ]
    
    def to_representation(self,instance):
        response = super(RenewGalaRequestSerializer, self).to_representation(instance)
        response['agreement_valid_doc'] = "https://bsgroup.org.in/" + "media" + "/" + response['agreement_valid_doc']

        response['ghar_patti_doc'] = "https://bsgroup.org.in/" + "media" + "/" + response['ghar_patti_doc']

        empty_dict = {}
        empty_dict['uid'] = response['uid']
        empty_dict['agreement_valid_doc'] = response['agreement_valid_doc']
        empty_dict['agreement_valid_start_date'] = response['agreement_valid_start_date']
        empty_dict['agreement_valid_end_date'] = response['agreement_valid_end_date']
        empty_dict['ghar_patti_doc'] = response['ghar_patti_doc']
        empty_dict['ghar_patti_start_date'] = response['ghar_patti_start_date']
        empty_dict['ghar_patti_end_date'] = response['ghar_patti_end_date']
        empty_dict['gala'] = response['gala']
        empty_dict['owner'] = response['owner']
        empty_dict['warehouse'] = response['warehouse']
        empty_dict['rental'] = response['rental']

        response['contract_details'] = empty_dict
        
        del response['uid']
        del response['agreement_valid_doc']
        del response['agreement_valid_start_date']
        del response['agreement_valid_end_date']
        del response['ghar_patti_doc']
        del response['ghar_patti_start_date']
        del response['ghar_patti_end_date']
        del response['gala']
        del response['owner']
        del response['warehouse']
        del response['rental']

        return response