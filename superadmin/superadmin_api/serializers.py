import re
from rest_framework import serializers

from account.models import (
    Investor,
    Rental,
    Farmer,
    User
)

from warehouse.models import (
    Property,
    Company,
)

from django.contrib.auth.models import Group
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from datetime import datetime, date
from warehouse.warehouse_api.serializers import (
    CompanySerializer
)

from contract.contract_api.serializers import (
    ContractInvestorSerializer
)
from account.models import (
    User,
    Investor,
    Rental
)
# from contract.models import (
#     Investor as ContractInvestor,
#     Rental as ContractRental,
#     Farmer as ContractFarmer

# )





class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = User.EMAIL_FIELD

    def validate(self, attrs):
        email = attrs.get("email", None)
        password = attrs.get("password", None)
        try:
            user_instance = User.objects.get(email__iexact=email)
            
        except Exception as exception:
            return {
                "status":status.HTTP_401_UNAUTHORIZED,
                "error_status":True,
                "error":"User is not exists.Please Register first!"
            }
        user = authenticate(email=email, password=password)
        if user is not None:
            if user_instance.is_superuser:
                refresh = self.get_token(user)
                
                return {
                    "status":status.HTTP_200_OK,
                    "error_status":False,
                    "refresh":str(refresh),
                    "access":str(refresh.access_token),
                    "username":user_instance.username,
                    "email":user_instance.email,
                    "user_uid":user.user_uid
                }
            else:
                return {
                    'status':status.HTTP_400_BAD_REQUEST,
                    'error_status':True,
                    'response':"You are not authorized to access"
            }
        elif user is None:
            return {
                "status":status.HTTP_401_UNAUTHORIZED,
                "error_status":True,
                "error":"Incorrect Password!"
            }
             
    @classmethod
    def get_token(cls, user):
        token = super(MyTokenObtainPairSerializer, cls).get_token(user)
        token['username'] = user.username
        return token
        

# class RegisterSerializer(serializers.ModelSerializer):
#     email = serializers.EmailField(
#             required=True,
#             validators=[UniqueValidator(queryset=User.objects.all())]
#             )
#     password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
#     password2 = serializers.CharField(write_only=True, required=True)
#     mobile_number = serializers.CharField(write_only=True, required=True,validators=[UniqueValidator(queryset=Profile.objects.all())])
#     birth_date = serializers.DateField(write_only=True, required=True)
#     gender = serializers.CharField(write_only=True, required=True)
#     source = serializers.CharField(write_only=True, required=True)

#     class Meta:
#         model = User
#         fields = ('username', 'password', 'password2', 'email','mobile_number','birth_date','gender','source')

    # def validate(self, attrs):
    #     today = date.today()
    #     birthdate = datetime.strptime(str(attrs['birth_date']),"%Y-%m-%d")
    #     age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))     
    #     pass_regex1 = re.search(passObj, attrs['password'])
    #     pass_regex2 = re.search(passObj, attrs['password2'])

    #     if not pass_regex1 and not pass_regex2:
    #         raise serializers.ValidationError({"password": "Invalid Password!"})
    #     elif age <= 18: 
    #         raise serializers.ValidationError({"birth_date": "Age should be 18 above!"})
    #     elif attrs['password'] != attrs['password2']:
    #         raise serializers.ValidationError({"password": "Password fields didn't match."})
    #     return attrs
        
    # def create(self, validated_data):
    #     user = User.objects.create(
    #         username=validated_data['username'],
    #         email=validated_data['email'],
    #     )
    #     user.set_password(validated_data['password'])
    #     user.save()
    #     profile = Profile.objects.create(
    #         user = user,
    #         mobile_number = validated_data['mobile_number'],
    #         birth_date = validated_data['birth_date'],
    #         gender = validated_data['gender'],
    #         source = validated_data['source'],
    #     )
    #     profile.save()
    #     wallet_instance = Wallet.objects.create(user=profile)
    #     wallet_instance.save()
    #     return user





class InvestorDetailSerializer(serializers.ModelSerializer):
    contract_url = serializers.SerializerMethodField()
    class Meta:
        model = Investor
        fields = ['user_uid','username','email','first_name','last_name',
        'phone','address','city','zip_code','birth_date','contract_url']
    
    def get_contract_url(self,instance):
        return instance.get_investor_url()
    

class RentalDetailSerializer(serializers.ModelSerializer):
    # contract_url = serializers.SerializerMethodField()
    class Meta:
        model = Rental
        fields = ['user_uid','username','email','first_name','last_name',
        'phone','address','city','zip_code','birth_date']

class FarmerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farmer
        fields = ['user_uid','username','email','first_name','last_name',
        'phone','address','city','zip_code','birth_date']


class RemainingPropertySerializer(serializers.ModelSerializer):
    
    # survey_number = serializers.CharField(source = "property_survey_number")
    # total_remaining_galas = serializers.IntegerField()
    class Meta:
        model = Property
        fields = ['uid','property_name',]

    # def to_representation(self,instance):
    #     data = super(RemainingPropertySerializer,self).to_representation(instance)
    #     if data['total_remaining_galas'] == None:
    #         data['total_remaining_galas'] = 0
    #     return data



    # def validate(self,data):
    #     if data['total_remaining_galas'] == 'null':
    #         return data['total_remaining_galas'] == 0
    #     'phone','address','city','zip_code','birth_date','contract_url']
    
    # def get_contract_url(self,instance):
    #     return instance.get_investor_url()

