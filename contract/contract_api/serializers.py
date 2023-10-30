from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from datetime import datetime
from contract.models import (
    Contract,
    Investor as ContractInvestor,
    Rental as ContractRental,
    Farmer as ContractFarmer,
)
from warehouse.models import (
    Property
)
from warehouse.warehouse_api.serializers import (
    GalaSerializer,
    FarmerGalaSerializer,
    RentalPropertyGalaSerializer,
    FarmerGalaDetailSerializer,
    InvestorPropertyGalaSerializer

    # FarmerGalaSerializer
)

from account.models import (
    Investor as AccountInvestor,
    Investor,
    Rental,
    UserAndInvestor,
    Farmer,
    Owner

)

# from account.account_api.serializers import (
#     OwnerSeriliazer
# )

from warehouse.models import (
    Gala
)
from rest_framework.response import Response
from django.core.validators import FileExtensionValidator

from django.core.exceptions import ValidationError

class RentalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rental
        fields = ['user_uid','username','email','first_name','last_name']

class UserAndInvestorSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAndInvestor
        fields = ['user_uid','username','email','first_name','last_name']

class UserInvestorSerializer(serializers.ModelSerializer):
    # investor_contract = ContractInvestorSerializer(many=True)
    class Meta:
        model = Investor
        fields = ['user_uid','username','email','phone','address','city','zip_code','birth_date']

class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = "__all__"


class ContractInvestorSerializer(serializers.ModelSerializer):
    # gala = GalaSerializer()
    owner = UserInvestorSerializer()
    class Meta:
        model = ContractInvestor
        fields = ['owner','user','gala','agreement_type']


class RentalWarehouseContractSerializer(serializers.ModelSerializer):
    owner = UserInvestorSerializer()
    class Meta:
        model = ContractRental
        fields =['gala','owner','user','agreement_type','agreement_valid_start_date','agreement_valid_end_date']


    def to_representation(self,instance):
        data = super(RentalWarehouseContractSerializer,self).to_representation(instance)

        if data['agreement_valid_start_date'] is not None:
            data['agreement_valid_start_date'] = datetime.strptime(data['agreement_valid_start_date'],"%Y-%m-%d").strftime("%d %b, %Y")

        if data['agreement_valid_end_date'] is not None:
            data['agreement_valid_end_date'] = datetime.strptime(data['agreement_valid_end_date'],"%Y-%m-%d").strftime("%d %b, %Y")

        return data



class ContractRentalSerializer(serializers.ModelSerializer):
    gala = GalaSerializer()
    # owner = UserAndInvestorSerializer()
    # user = RentalSerializer()
    class Meta:
        model = ContractRental
        fields = ['owner','user','gala','agreement_type','agreement_valid_start_date','agreement_valid_end_date']

    
    def to_representation(self,instance):
        data = super(RentalWarehouseContractSerializer,self).to_representation(instance)

        if data['agreement_valid_start_date'] is not None:
            data['agreement_valid_start_date'] = datetime.strptime(data['agreement_valid_start_date'],"%Y-%m-%d").strftime("%d %b, %Y")

        if data['agreement_valid_end_date'] is not None:
            data['agreement_valid_end_date'] = datetime.strptime(data['agreement_valid_end_date'],"%Y-%m-%d").strftime("%d %b, %Y")

        return data


# class GetGalaFromContractRentalSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ContractRental
#         fields = "__all__"


class CreateContractWithFarmer(serializers.ModelSerializer):
    warehouse = serializers.CharField()
    user = serializers.CharField()
    class Meta:
        model = ContractFarmer
        fields = ['warehouse','user']
    

    def validate(self, attrs):
        try:
            attrs['warehouse'] = Property.objects.get(uid=attrs['warehouse'])
            attrs['user'] = Farmer.objects.get(user_uid=attrs['user'])
            return attrs
        except Property.DoesNotExist:
            raise ValidationError("Property not found")
        
        except Farmer.DoesNotExist:
            raise ValidationError("Farmer not found")
        
    def create(self, validated_data):
        contract_instance = ContractFarmer.objects.create(
            warehouse = validated_data['warehouse'],
            user = validated_data['user']
        )      
        return contract_instance
        
class ContractInvestorPostSerializer(serializers.ModelSerializer):
    gala = serializers.CharField()
    user = serializers.CharField()
    class Meta:
        model = ContractInvestor
        fields = ['gala','user']


    def validate(self, attrs):
        attrs['user'] = get_object_or_404(AccountInvestor,user_uid = attrs['user'])
        attrs['gala'] = Gala.objects.get(uid = attrs['gala'])
        return attrs


    def create(self,validated_data):
    
        create_investor_contract = ContractInvestor(
            gala = validated_data['gala'],
            user= validated_data['user']
        )
        # create_investor_contract.clean()
        create_investor_contract.save()
        return create_investor_contract


# class UserFarmerSerializer(serializers.ModelSerializer):
#     # investor_contract = ContractInvestorSerializer(many=True)
#     class Meta:
#         model = Farmer
#         fields = ['user_uid','username']

# class FarmerRentalSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Rental
#         fields = ['user_uid','username']

       
class FarmerContractSerializer(serializers.ModelSerializer):
    # gala = serializers.CharField(source="gala.gala_number")
    # owner = serializers.StringRelatedField()
    # user = serializers.StringRelatedField()
    # gala = FarmerGalaSerializer()
    # owner = UserFarmerSerializer()
    # user = FarmerRentalSerializer()
    class Meta:
        model = ContractRental
        fields = ['uid','gala','owner','user','agreement_type','agreement_valid_start_date','agreement_valid_end_date','ghar_patti_start_date','ghar_patti_end_date']

    def to_representation(self,instance):
        data = super(FarmerContractSerializer,self).to_representation(instance)

        if data['agreement_valid_start_date'] is not None:
            data['agreement_valid_start_date'] = datetime.strptime(data['agreement_valid_start_date'],"%Y-%m-%d").strftime("%d %b, %Y")

        if data['agreement_valid_end_date'] is not None:
            data['agreement_valid_end_date'] = datetime.strptime(data['agreement_valid_end_date'],"%Y-%m-%d").strftime("%d %b, %Y")

        if data['ghar_patti_start_date'] is not None:
            data['ghar_patti_start_date'] = datetime.strptime(data['ghar_patti_start_date'],"%Y-%m-%d").strftime("%d %b, %Y")


        if data['ghar_patti_end_date'] is not None:
            data['ghar_patti_end_date'] = datetime.strptime(data['ghar_patti_end_date'],"%Y-%m-%d").strftime("%d %b, %Y")

        return data


from datetime import datetime
from dateutil.relativedelta import relativedelta

class ContractWithRentalSerializer(serializers.ModelSerializer):
    gala = serializers.CharField(max_length=50)
    owner = serializers.CharField(max_length=50)
    user = serializers.CharField(max_length=50)
    agreement_valid_doc = serializers.FileField(validators=[FileExtensionValidator(['pdf'])])
    ghar_patti_doc = serializers.FileField(validators=[FileExtensionValidator(['pdf'])])
    agreement_valid_start_date = serializers.DateField()
    locking_period = serializers.IntegerField()
    agreement_valid_end_date = serializers.DateField()
    ghar_patti_start_date = serializers.DateField()
    ghar_patti_end_date = serializers.DateField()

    class Meta:
        model = ContractRental
        fields = "__all__"
        kwargs = {"gala":{"required": True}}
    
    def validate(self,attrs):
        try:
            attrs['gala'] = Gala.objects.get(uid = attrs['gala']).id
            attrs['user'] = Rental.objects.get(user_uid = attrs['user']).id
            attrs['owner'] = UserAndInvestor.objects.get(user_uid = attrs['owner']).id
            return attrs
        except Exception as exception:
            raise ValidationError({"errors":(str(exception))})
        
    def create(self,validated_data):
        # print(validated_data['locking_period'])
        # print(validated_data['agreement_valid_start_date'])
        get_agreement_valid_start_date = datetime.strptime(str(validated_data['agreement_valid_start_date']),"%Y-%m-%d")
        get_locking_period = get_agreement_valid_start_date + relativedelta(years=int(validated_data['locking_period']))

        contract_rental_instance = ContractRental.objects.create(
            gala_id = validated_data['gala'],
            user_id = validated_data['user'],
            owner_id = validated_data['owner'],
            agreement_valid_doc = validated_data['agreement_valid_doc'],
            ghar_patti_doc = validated_data['ghar_patti_doc'],
            locking_period  = get_locking_period,
            agreement_valid_start_date = validated_data['agreement_valid_start_date'],
            agreement_valid_end_date = validated_data['agreement_valid_end_date'],
            ghar_patti_start_date = validated_data['ghar_patti_start_date'],
            ghar_patti_end_date = validated_data['ghar_patti_end_date']
        )
        return contract_rental_instance
    

class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Owner
        fields = ['user_uid','username','email','first_name','last_name']

# class RentalSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Owner
#         fields = ['username','first_name','last_name']

class RentalPropertyFromContract(serializers.ModelSerializer):
    gala = RentalPropertyGalaSerializer()
    renew_status = serializers.CharField()
    request_count = serializers.IntegerField()
    leave_request_count = serializers.IntegerField()
    leave_request_status = serializers.CharField()
    to_be_renewed = serializers.BooleanField()
    # agreement_valid_doc = serializers.FileField(use_url=True)
    owner = UserAndInvestorSerializer()
    # owner = serializers.StringRelatedField()
    # gala = serializers.StringRelatedField()
    # company_name = serializers.CharField()
    class Meta:
        model = ContractRental
        # fields = "__all__"
        exclude = ['id','created_at','updated_at','user','polymorphic_ctype']
    
    def to_representation(self,instance):
        response = super(RentalPropertyFromContract, self).to_representation(instance)
        response['agreement_valid_start_date'] = datetime.strptime(response['agreement_valid_start_date'],"%Y-%m-%d").strftime("%d %b, %Y")
        response['agreement_valid_end_date'] = datetime.strptime(response['agreement_valid_end_date'],"%Y-%m-%d").strftime("%d %b, %Y")
        response['ghar_patti_start_date'] = datetime.strptime(response['ghar_patti_start_date'],"%Y-%m-%d").strftime("%d %b, %Y")
        response['ghar_patti_end_date'] = datetime.strptime(response['ghar_patti_end_date'],"%Y-%m-%d").strftime("%d %b, %Y")
        response['locking_period'] = datetime.strptime(response['locking_period'],"%Y-%m-%d").strftime("%d %b, %Y")
        # response['agreement_type'] = response['agreement_type'].replace("_"," ")
        response['agreement_valid_doc'] = "https://bsgroup.org.in" + response['agreement_valid_doc']
        response['ghar_patti_doc'] = "https://bsgroup.org.in" + response['ghar_patti_doc']

        agreement_end_date = response['agreement_valid_end_date']
        print(response['renew_status'])
        # agreement_end_date = "2023-05-31"
        agreement_end_date = datetime.strptime(agreement_end_date,'%d %b, %Y').date()
        relevent_date = agreement_end_date - datetime.today().date()
        # print(response['renew_status'])
        # if relevent_date.days >= 0 and relevent_date.days <= 90 or response['renew_status'] != None and response['renew_status'] == "Reject":
        #     print(311)
        #     response['to_be_renewed'] = True
        # elif response['renew_status'] != None and response['renew_status']=="Pending" or  response['leave_request_count'] >= 1:
        #     response['to_be_renewed'] = False
        #     print(315)
        # else:
        #     response['to_be_renewed'] = False
        # if relevent_date.days >= 0 and relevent_date.days <= 90 or relevent_date.days <= 0 and relevent_date.days >= -30 :
        #     response['to_be_renewed'] = True
        #     try:
        #         if response['renew_status'] == "Pending" and response['renew_status'] != None or response['leave_request_count'] >= 1 and response['leave_request_status'] == "Pending":
        #             response['to_be_renewed'] = False
        #         if response['renew_status'] == "Reject" or response['leave_request_status'] == "Reject":
        #             response['to_be_renewed'] = True
        #     except Exception as exception:
        #         pass
        # elif response['renew_status'] == "Pending": 
        #     response['to_be_renewed'] = False
        # else:
        #     response['to_be_renewed'] = False
        
        # else:
        #     response['to_be_renewed'] = False
        # else:
        #     response['to_be_renewed'] = True

            # try:
            #     if response['renew_status'] == "Pending":
            #         response['to_be_renewed'] = False

            #     if response['renew_status'] == "Reject":
            #         response['to_be_renewed'] = True
            # except Exception as exception:
            #     pass

        # elif response['renew_status'] == "Pending":
        #     response['to_be_renewed'] = False
            
        # else:
        #     response['to_be_renewed'] = False
        

        
        # del response['renew_status']
        # del response['request_count']
            
        return response

class ContractFarmerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractFarmer
        fields = ['uid','warehouse','owner','user','agreement_type']



#for farmer
class FarmerRentalGalaDetailSerializer(serializers.ModelSerializer):
    gala = FarmerGalaDetailSerializer()
    # agreement_valid_doc = serializers.FileField(use_url=True)
    owner = UserAndInvestorSerializer()
    user = RentalSerializer()
    # owner = serializers.StringRelatedField()
    # gala = serializers.StringRelatedField()
    # company_name = serializers.CharField()
    class Meta:
        model = ContractRental
        # fields = "__all__"
        exclude = ['id','created_at','updated_at','polymorphic_ctype']
    
    def to_representation(self,instance):
        response = super(FarmerRentalGalaDetailSerializer, self).to_representation(instance)
        response['agreement_valid_start_date'] = datetime.strptime(response['agreement_valid_start_date'],"%Y-%m-%d").strftime("%d %b, %Y")
        response['agreement_valid_end_date'] = datetime.strptime(response['agreement_valid_end_date'],"%Y-%m-%d").strftime("%d %b, %Y")
        response['ghar_patti_start_date'] = datetime.strptime(response['ghar_patti_start_date'],"%Y-%m-%d").strftime("%d %b, %Y")
        response['ghar_patti_end_date'] = datetime.strptime(response['ghar_patti_end_date'],"%Y-%m-%d").strftime("%d %b, %Y")
        return response


#for Investor
class InvestorRentalGalaDetailSerializer(serializers.ModelSerializer):
    gala = InvestorPropertyGalaSerializer()
    # agreement_valid_doc = serializers.FileField(use_url=True)
    owner = UserAndInvestorSerializer()
    user = RentalSerializer()
    # owner = serializers.StringRelatedField()
    # gala = serializers.StringRelatedField()
    # company_name = serializers.CharField()
    class Meta:
        model = ContractRental
        # fields = "__all__"
        exclude = ['id','created_at','updated_at','polymorphic_ctype']
    
    def to_representation(self,instance):
        response = super(InvestorRentalGalaDetailSerializer, self).to_representation(instance)
        if response['agreement_valid_start_date'] is not None:
            response['agreement_valid_start_date'] = datetime.strptime(response['agreement_valid_start_date'],"%Y-%m-%d").strftime("%d %b, %Y")

        if response['agreement_valid_end_date'] is not None:
            response['agreement_valid_end_date'] = datetime.strptime(response['agreement_valid_end_date'],"%Y-%m-%d").strftime("%d %b, %Y")

        if response['ghar_patti_start_date'] is not None:
            response['ghar_patti_start_date'] = datetime.strptime(response['ghar_patti_start_date'],"%Y-%m-%d").strftime("%d %b, %Y")


        if response['ghar_patti_end_date'] is not None:
            response['ghar_patti_end_date'] = datetime.strptime(response['ghar_patti_end_date'],"%Y-%m-%d").strftime("%d %b, %Y")

        return response



        # response['agreement_valid_start_date'] = datetime.strptime(response['agreement_valid_start_date'],"%Y-%m-%d").strftime("%d %b, %Y")
        # response['agreement_valid_end_date'] = datetime.strptime(response['agreement_valid_end_date'],"%Y-%m-%d").strftime("%d %b, %Y")
        # response['ghar_patti_start_date'] = datetime.strptime(response['ghar_patti_start_date'],"%Y-%m-%d").strftime("%d %b, %Y")
        # response['ghar_patti_end_date'] = datetime.strptime(response['ghar_patti_end_date'],"%Y-%m-%d").strftime("%d %b, %Y")
        return response


class FreeGalaDetailSerializer(serializers.ModelSerializer):
    pass