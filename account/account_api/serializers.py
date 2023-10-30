import uuid, random, urllib,re
from rest_framework import serializers
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.backends import TokenBackend
from django.contrib.auth import password_validation
from account.models import (
    Investor as AccountInvestor,
    Investor,
    Rental as AccountRental,
    Rental,
    Farmer,
    User,
    Owner,
    UserAndInvestor
)
from contract.contract_api.serializers import (
    ContractRentalSerializer,
    ContractInvestorSerializer,
    RentalWarehouseContractSerializer,
    FarmerContractSerializer,
    ContractFarmerSerializer
)
from warehouse.warehouse_api.serializers import (
    GalaSerializer,
    LiveAndLicenseContractRentalSerializer
)
from django.urls import reverse
from django.db.models import (
    Q
)
from contract.models import (
    Rental as ContractRental,
    Investor as ContractInvestor
)
from django.forms.models import model_to_dict
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework.serializers import CharField
from rest_framework.response import Response
from django.http import JsonResponse

from warehouse.models import (
    Company,
    Property,
    Gala,
)
from datetime import datetime

from datetime import datetime
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from fcm_django.models import FCMDevice
from jwt_authentication.models import (
    TokenAuthentication
)

class TokenRefreshLifetimeSerializer(TokenRefreshSerializer):

    def validate(self, attrs):
        try:
            data = super().validate(attrs)
            token = RefreshToken(attrs['refresh'])
            new_access = str(token.access_token)
            author, created = TokenAuthentication.objects.get_or_create(user_id = token.payload['user_id'],defaults={'access': new_access})
            if not created:
                author.access = new_access
                author.save()
            get_fcm_device = FCMDevice.objects.get(user_id = token.payload['user_id'])
            get_fcm_device.active = False
            get_fcm_device.save()
            token.blacklist()
            # print(refresh.access_token)
            # print(refresh.__dir__())
            # print()
            # data['access_token'] = refresh['access_token']
            # data['lifetime'] = int(refresh.access_token.lifetime.total_seconds())
            # user_instance = User.objects.get(id = )
            return {
                "status":status.HTTP_200_OK,
                "success":True,
                "error_status":False,
            }
        except Exception as exception:
            return {
                'status':status.HTTP_200_OK,
                "success":True,
                'error_status':False,
            }
        # return data

def build_url(*args, **kwargs):
    get = kwargs.pop('get', {})
    url = reverse(*args, **kwargs)
    if get:
        url += '?' + urllib.parse.urlencode(get)
    return url

def get_companies():
    get_company = Company.objects.all()
    return get_company


def get_rental_instance():
        get_rental_pk = Group.objects.get(name__icontains="rental")
        return get_rental_pk.id

def get_farmer_instance():
        get_farmer_pk = Group.objects.get(name__icontains="Farmer")
        return get_farmer_pk.id

def get_investor_instance():
        get_tenant_pk = Group.objects.get(name__icontains="Investor")
        return get_tenant_pk.id


class CutomTokenSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls,instance):
        token = super().get_token(instance)

        token['name'] =instance.username
        token['email'] = instance.email
        return token


class InvestorUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Investor
        fields = ['first_name', 'last_name', 'email','phone','address','city','zip_code','birth_date']
        write_only_fields = ('password',)
        extra_kwargs = {
            'first_name':{"required":True},
            "last_name":{"required":True},
            "phone":{"required":True},
            "address":{"required":True},
            "city":{"required":True},
            "zip_code":{"required":True},
            "birth_date":{"required":True}
        }

    
    def create(self, validated_data):
        user = Investor.objects.create(
            username = validated_data['first_name'].lower(),
            email = validated_data['email'],
            first_name = validated_data['first_name'],
            last_name = validated_data['last_name'],
            birth_date = validated_data['birth_date'],
            address = validated_data['address'],
            phone = validated_data['phone'],
            city = validated_data['city'],
            zip_code = validated_data['zip_code'],
        )
        set_password = validated_data['first_name'] + "@12345"
        user.set_password(set_password)
        user.groups.set([get_investor_instance()])
        companies = get_companies()
        user.belong_to.add(*companies)
        user.save()
        return user


class RentalUserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(max_length=25,min_length=8,write_only=True)
    password = serializers.CharField(max_length=25,min_length=8)

    class Meta:
        model = Rental
        fields = ['password','confirm_password','first_name', 'last_name', 'email','phone','address']
        write_only_fields = ('password','phone',)
        extra_kwargs = {
            'password': {'write_only': True},
            'first_name':{'error_messages': {'blank': 'first_name field may not be blank'},'required':True},
            "last_name":{'error_messages': {'blank': 'last_name field may not be blank'},"required":True},
            "phone":{'error_messages': {'blank': 'phone field may not be blank'},"required":True},
            "address":{'error_messages': {'blank': 'address field may not be blank'},"required":True},
            "email":{'error_messages': {'blank': 'email field may not be blank'},"required":True},
            "confirm_password":{'error_messages': {'blank': 'confirm_password field may not be blank'},"required":True}
        }

    def validate(self,attrs):
        regex_for_password = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
        regex_for_email = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
        regex_for_name = re.compile("^([A-Za-z])")
        passObj = re.compile(regex_for_password)
        pass_regex1 = re.search(passObj, attrs['password'])
        if not pass_regex1:
            raise serializers.ValidationError("Password should include a capital letter, a special character and numbers!")
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("password is not matched!")
        if not re.fullmatch(regex_for_email, attrs['email']):
            raise serializers.ValidationError("email address is not valid!")
        if len(attrs['phone']) > 10 or len(attrs['phone']) < 10:
            print(attrs['phone'])
            raise serializers.ValidationError("phone number is not valid!")
        
        first_name_regex = re.search(regex_for_name, attrs['first_name'])
        if not first_name_regex:
            raise serializers.ValidationError("first_name should contains only letters!")
        last_name_regex = re.search(regex_for_name, attrs['last_name'])
        if not last_name_regex:
            raise serializers.ValidationError("last_name should contains only letters!")
        # address_regex = re.search(regex_for_name, attrs['address'])
        # if not address_regex:
        #     raise serializers.ValidationError({"address": "address should contains only letters!"})
        return attrs
    


    def create(self, validated_data):
        set_username = validated_data['first_name']
        user = Rental.objects.create(
            username = set_username.lower(),
            first_name = validated_data['first_name'],
            last_name = validated_data['last_name'],
            phone = validated_data['phone'],
            address =  validated_data['address'],
            email = validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.groups.set([get_rental_instance()])
        companies = get_companies()
        user.belong_to.add(*companies)
        user.save()
        return user


class FarmerUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farmer
        fields = ['first_name', 'last_name', 'phone','address','birth_date']
        write_only_fields = ('password',)
        extra_kwargs = {
            'first_name':{"required":True},
            "last_name":{"required":True},
            "phone":{"required":True},
            "address":{"required":True},
            "birth_date":{"required":True}
        }
    
    def create(self,validate_data):
        # validate_data['username'] = validate_data['first_name'] + " " + validate_data['last_name'],
        # validate_data['email'] = validate_data['username'] + "@gmail.com"
        # for i,v in validate_data.items():
        #     print(i,v)
        set_email = validate_data['first_name'] + validate_data['last_name']  + "@gmail.com"
        farmer_user = Farmer.objects.create(
            username = validate_data['first_name'].lower(),
            email = set_email.lower(),
            first_name = validate_data['first_name'],
            last_name = validate_data['last_name'],
            birth_date = validate_data['birth_date'],
            address = validate_data['address'],
            phone = validate_data['phone'],
        )
        set_password = farmer_user.username + "@12345"
        farmer_user.set_password(set_password)
        farmer_user.groups.set([get_farmer_instance()])
        companies = get_companies()
        farmer_user.belong_to.add(*companies)
        farmer_user.save()
        return farmer_user
        
class GroupSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Group
        fields = ['id','name']


class UserRentalSerializer(serializers.ModelSerializer):
    rental_contract = ContractRentalSerializer(many=True)
    class Meta:
        model = Rental
        fields = ['user_uid','username','email','phone','address','city','zip_code','birth_date','rental_contract']
    
class UserInvestorSerializer(serializers.ModelSerializer):
    investor_contract = ContractInvestorSerializer(many=True)
    class Meta:
        model = Investor
        fields = ['user_uid','username','email','phone','address','city','zip_code','birth_date','investor_contract']
    
    def to_representation(self,instance):
        data = super(UserInvestorSerializer, self).to_representation(instance)
        data['numbers_of_gala'] = len(data['investor_contract'])
        return data


class RentalUserPutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rental
        fields = ['email','first_name','last_name', 'phone','address']
        extra_kwargs = {
            'first_name':{"required":True},
            "last_name":{"required":True},
            "phone":{"required":True},
            "address":{"required":True}
        }
    

    def validate(self,attrs):
        regex_for_name = re.compile("^([A-Za-z])")
        first_name_regex = re.search(regex_for_name, attrs['first_name'])
        if not first_name_regex:
            raise serializers.ValidationError({"first_name": "first_name should contains only letters!"})
        last_name_regex = re.search(regex_for_name, attrs['last_name'])
        if not last_name_regex:
            raise serializers.ValidationError({"last_name": "last_name should contains only letters!"})
        address_regex = re.search(regex_for_name, attrs['address'])
        if not address_regex:
            raise serializers.ValidationError({"address": "address should contains only letters!"})
        return attrs
        # if attrs['password'] != attrs['confirm_password']:
        #     raise serializers.ValidationError({"password": "confirm password must be matched with password"})
        # if not re.fullmatch(regex_for_email, attrs['email']):
        #     raise serializers.ValidationError({"email": "Email is not a valid email address"})
        if len(attrs['phone']) > 10 or len(attrs['phone']) < 10:
            raise serializers.ValidationError({"phone": "phone number is not valid!"})
        return attrs
    
    # def validate_first_name(self,value):
    #     if value == "":
    #         print(value)
    #         raise serializers.ValidationError({"first_name": "first_name may not be blank"})
    #     return value
    
    # def validate(self, attrs):
    #     if validate['first_name'] == "":
    #         raise ValidationError
    #     pass


class ResetPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    class Meta:
        fields = ['email']


class ResetPasswordSerializer(serializers.Serializer):
    """
    Reset Password Serializer.
    """

    password = serializers.CharField(write_only=True , min_length=1,)

    class Meta:
        field = ("password")

    def validate(self, data):
        """
        Verify token and encoded_pk and then set new password.
        """
        password = data.get("password")
        token = self.context.get("kwargs").get("token")
        encoded_pk = self.context.get("kwargs").get("encoded_pk")

        if token is None or encoded_pk is None:
            raise serializers.ValidationError("Missing data.")

        pk = urlsafe_base64_decode(encoded_pk).decode()
        user = User.objects.get(pk=pk)
        if not PasswordResetTokenGenerator().check_token(user, token):
            raise serializers.ValidationError("The reset token is invalid")

        user.set_password(password)
        user.save()
        return data


class RentalWarehouseAndGalaSerializer(serializers.ModelSerializer):
    total_number_of_galas = serializers.IntegerField()
    # get_total_warehouse = serializers.IntegerField()
    total_number_of_warehouse = serializers.IntegerField()
    url = serializers.SerializerMethodField()
    
    # total_warehouse = serializers.CharField()
    class Meta:
        model = Rental
        fields = ["id","user_uid","first_name","last_name","username","total_number_of_galas","total_number_of_warehouse","url"]
    


    def get_url(self,instance):
        get_company_type = self.context.get("company_type")
        url = build_url('get-rental-warehouse-detail', get={'company_type': get_company_type},kwargs={"uuid":instance['user_uid']})
        return url
    
    # def to_representation(self,instance):
    #     data = super(RentalWarehouseAndGalaSerializer, self).to_representation(instance)
    #     if data['total_number_of_galas'] is None:
    #         data['total_number_of_galas'] = 0
    #     return data

class RentalWarehouseAndGalaDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rental
        fields = ['user_uid','username',"email","first_name","last_name","phone","address","city","zip_code","birth_date"]

    
    def to_representation(self,instance):
        data = super(RentalWarehouseAndGalaDetailSerializer,self).to_representation(instance)
        user_uid = self.context.get('user_uid')
        data['contract'] = ContractRental.objects.filter(user__user_uid = user_uid).values(
            "gala__uid","gala__gala_number","owner__username","user__username","owner__groups__name",
            "agreement_type","agreement_valid_start_date",'agreement_valid_end_date',
            "agreement_valid_doc","ghar_patti_doc","ghar_patti_start_date","ghar_patti_end_date",
            "gala__warehouse__property_name"
        )
        # print(data['contract'][0]['agreement_valid_start_date'])
        # change_date_format = 
        # if data['agreement_valid_start_date'] != None:
        #     data['agreement_valid_start_date'] = datetime.strptime(data['agreement_valid_start_date'],"%Y-%m-%d").strftime("%d %b, %Y")

        # if data['agreement_valid_end_date'] is not None:
        #     data['agreement_valid_end_date'] = datetime.strptime(data['agreement_valid_end_date'],"%Y-%m-%d").strftime("%d %b, %Y")

        # if data['ghar_patti_start_date'] is not None:
        #     data['ghar_patti_start_date'] = datetime.strptime(data['ghar_patti_start_date'],"%Y-%m-%d").strftime("%d %b, %Y")


        # if data['ghar_patti_end_date'] is not None:
        #     data['ghar_patti_end_date'] = datetime.strptime(data['ghar_patti_end_date'],"%Y-%m-%d").strftime("%d %b, %Y")


        # data['contract']['owner__username'] = data['contract']['owner__username'] + data['contract']['owner__groups__name']
        return data



class FarmerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farmer
        fields = ['id','user_uid','username','email','first_name','last_name','phone','address','birth_date']
    
    def to_representation(self,instance):
        
        response  = super(FarmerListSerializer, self).to_representation(instance)
        response['username'] = response['username'] + " " + "(Farmer)"

        return response


        
class ChangePasswordSerializer(serializers.ModelSerializer):
    new_password  = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password  = serializers.CharField(write_only=True, required=True)
    old_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('new_password', 'confirm_password', 'old_password')

    def validate_old_password(self, value):
        # user = self.context['request'].user

        token = self.context['request'].META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
        get_logged_in_user = valid_data['user_id']
        user = Rental.objects.get(pk=get_logged_in_user)
        if not user.check_password(value):
            raise serializers.ValidationError(
                ('Your old password was entered incorrectly. Please enter it again.')
            )
        return value

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({'confirm_password':("The two password fields didn't match.")})
        password_validation.validate_password(data['new_password'], self.context['request'].user)
        return data

    def save(self, **kwargs):
        password = self.validated_data['new_password']
        user = self.context['request'].user
        user.set_password(password)
        user.save()
        return user

class InvestorTokenSerializer(TokenObtainPairSerializer):
    username_field = User.EMAIL_FIELD

    def validate(self, attrs):
        email = attrs.get("email", None)
        print(email)
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
            if user_instance.groups.first().name == "Investor":
                refresh = self.get_token(user)
                return {
                    "status":status.HTTP_200_OK,
                    "error_status":False,
                    "refresh":str(refresh),
                    "access":str(refresh.access_token),
                    "username":user_instance.username,
                    "email":user_instance.email,
                    # "group":user.groups.first().name
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
        token = super(InvestorTokenSerializer, cls).get_token(user)
        token['username'] = user.username
        return token
        

# @classmethod
def get_token(self,instance):
    refresh = RefreshToken.for_user(instance)
    data = {}
    data['refresh'] = str(refresh)
    data['access'] = str(refresh.access_token)
    self.token = data
    return self.token

class RentalTokenSerializer(TokenObtainPairSerializer):

    username_field = User.EMAIL_FIELD
    
    # @classmethod
    # def get_token(cls, user):
    #     token = super(RentalTokenSerializer, cls).get_token(user)
    #     token['username'] = user.username
    #     return token
    # username_field = User.EMAIL_FIELD

    # def validate(self, attrs):
    #     email = attrs.get("email", None)
    #     password = attrs.get("password", None)
    #     data = dict()
    #     get_data = super(TokenObtainPairSerializer, self).validate(attrs)
    #     check_email = User.objects.get(email__iexact = email)
    #     print(check_email)
    #     if check_email:
            
    #         user = authenticate(email=email, password=password)
    #         refresh = self.get_token(user)
    #         data['status'] = status.HTTP_200_OK
    #         data['success'] = True
    #         data['error_status'] = False
    #         data['refresh'] = str(refresh)
    #         data['access'] = str(refresh.access_token)
    #         data['username'] = user.username.title()
    #         data['email']=user.email
    #         return data
    #     else:
    #         data['status'] = status.HTTP_HTTP_401_UNAUTHORIZED401
    #         data['success'] = False
    #         data['error_status'] = True
    #         data['response'] = "Incorrect password!"
    #         return data

            
        # except (CustomUser.DoesNotExist, ValueError, TypeError, OverflowError):
        #     
        
    # @classmethod
    # def get_token(cls, user):
    #     if user:
    #         token = super(MyTokenObtainPairSerializer, cls).get_token(user)
    #         token['username'] = user.username
    #         return token
    #     else:
    #         raise InvalidToken("User is not enabled.")

    # def validate(self, attrs):
    #     email = attrs.get("email",None)
    #     print(email)
    #     password = attrs.get("password",None)

    #     try:
    #         check_email = User.objects.get(email__iexact = email)
    #         user = authenticate(email=email,password=password)
        
    #     except Exception as exception:
    #         context = {
    #             "status": status.HTTP_401_UNAUTHORIZED,
    #             "success":False,
    #             "error_status":True,
    #             "response":"User does not exist ! Please Register first !"
    #         }
    #         return context
    #         # return JsonResponse(context,status=status.HTTP_401_UNAUTHORIZED)

        
        
        
    #     if user is not None:
    #         if check_email.groups.first().name == "Rental":
    #             token = self.get_token(user)
    #             context =  {
    #                 "status":status.HTTP_200_OK,
    #                 "success":True,
    #                 "error_status":False,
    #                 "refresh":str(token),
    #                 "access":str(token.access_token),
    #                 "username":check_email.username,
    #                 "email":check_email.email,
    #                 # "group":user.groups.first().name
    #             }
    #             return context
    #             # return Response(context,status=status.HTTP_200_OK)
    #         else:
    #             context =  {
    #                 'status':status.HTTP_400_BAD_REQUEST,
    #                 "success":False,
    #                 'error_status':True,
    #                 'response':"You are not authorized to access"
    #             }
    #             return context
    #             # return Response(context,status=status.HTTP_400_BAD_REQUEST)
        
    #     elif user is None:
    #         context =  {
    #             'status':status.HTTP_400_BAD_REQUEST,
    #             "success":False,
    #             'error_status':True,
    #             'response':"Incorrect Password"
    #         }
    #         return context
            # return Response(context,status=status.HTTP_400_BAD_REQUEST)
        

 
class AccountInvestorListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountInvestor
        fields = ["user_uid","username"]

    def to_representation(self, instance):
        # print(instance.__dir__())
        data = super(AccountInvestorListSerializer,self).to_representation(instance)
        data['username'] = data['username'] + "-" + "("+ instance.email + ")"  + "-" + "Investor"
        return data

class AccountRentalListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountRental
        fields = ['user_uid','username']


    def to_representation(self,instance):
        data = super(AccountRentalListSerializer,self).to_representation(instance)
        data['username'] = data['username'] +"-"+ "(" + instance.email + ")" + "-" + "Rental"
        return data
         

class FarmerGalaDetailSerializer(serializers.ModelSerializer):
    # get_investor_contract = FarmerContractSerializer(many=True)
    class Meta:
        model = Farmer
        fields = ['user_uid','username','phone','address','city','zip_code','birth_date']
    
    def to_representation(self,instance):
        response = super(FarmerGalaDetailSerializer,self).to_representation(instance)
        response['get_investor_contract'] = ContractRental.objects.filter(
            gala__warehouse__uid=self.context.get("warehouse_uid")
            ).values(
                "uid","gala__gala_number","owner__username",
                "user__username","agreement_type","agreement_valid_start_date","agreement_valid_end_date",
                "ghar_patti_start_date","ghar_patti_end_date"
            )
        return response
    

class InvestorListViewSerializer(serializers.ModelSerializer):
    total_galas = serializers.IntegerField()
    total_rentals = serializers.IntegerField()
    total_remaining_galas = serializers.IntegerField()
    class Meta:
        model = AccountInvestor
        fields = [
            "user_uid","username","first_name","last_name","address","phone","address","email",
            "city","zip_code","birth_date","total_galas","total_rentals","total_remaining_galas"
        ]
    
    def to_representation(self,instance):
        response = super(InvestorListViewSerializer,self).to_representation(instance)
        response['username'] = response['first_name'] + " " + response['last_name']
        if response['total_rentals'] == None:
            response['total_rentals'] = 0
        if response['total_galas'] == None:
            response['total_galas'] = 0
        if response['total_remaining_galas'] == None:
            response['total_remaining_galas'] = 0
        # response['birth_date'] = datetime.strptime(response['birth_date'],"%Y-%m-%d").strftime("%d %b, %Y")
        return response

    def get_remaining_galas(self,instance):
        get_company_type = self.context.get("company_type")
        pass


class TestFarmerListSerializer(serializers.ModelSerializer):
    # get_farmer_contract = ContractFarmerSerializer(many=True)
    # warehouse_name = serializers.CharField()
    # remaining_gala = serializers.SerializerMethodField()
    # allotted_gala = serializers.SerializerMethodField()
    total_gala_count = serializers.IntegerField()
    remaining_gala_count = serializers.IntegerField()
    allotted_gala_count = serializers.IntegerField()
    class Meta:
        model = Farmer
        fields = ['user_uid','username','phone','address','city','zip_code','birth_date','total_gala_count',
                'remaining_gala_count','allotted_gala_count']
        # exclude = ['created_at']


    def to_representation(self,instance):
        data = super(TestFarmerListSerializer,self).to_representation(instance)
        print(instance.__dir__(),17)

        if data['total_gala_count'] is None:
            data['total_gala_count'] = 0
        
        if data['remaining_gala_count'] is None:
            data['remaining_gala_count'] = 0

        if data['allotted_gala_count'] is None:
            data['allotted_gala_count'] = 0
        return data

class ViewContractRentalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rental
        fields = ['user_uid','username']

class ViewContractUserInvestorSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAndInvestor
        fields = ['user_uid','username']



class ServiceRequestAccountRentalSerializer(serializers.ModelSerializer):
    rental_name = serializers.SerializerMethodField()
    date_of_joining = serializers.SerializerMethodField()
    date_of_birth = serializers.SerializerMethodField()
    class Meta:
        model = AccountRental
        fields = ['user_uid','email','rental_name','phone','address','city','date_of_birth','zip_code','date_of_joining']
    
    def get_rental_name(self,instance):
        return instance.first_name + " " + instance.last_name

    def get_date_of_joining(self,instance):
        get_date = instance.created_at.date()
        return datetime.strptime(str(get_date), "%Y-%m-%d").strftime("%d-%m-%Y")
    
    def get_date_of_birth(self,instance):
        get_date = instance.birth_date
        return datetime.strptime(str(get_date), "%Y-%m-%d").strftime("%d-%m-%Y")


class DashboardAccountRentalListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountRental
        fields = ['user_uid','username','first_name','last_name','email','phone']


    # def to_representation(self,instance):
    #     data = super(DashboardAccountRentalListSerializer,self).to_representation(instance)
    #     data['username'] = data['username'] +"-"+ "(" + instance.email + ")" + "-" + "Rental"
    #     return data


class FarmerUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farmer
        fields = ['first_name', 'last_name', 'phone','address','birth_date']


    def update(self,instance,validated_data):

        get_farmer_instance = Farmer.objects.get(
            user_uid = instance.user_uid
        )

        get_farmer_instance.username = validated_data['first_name'].lower() + validated_data['last_name'].lower()
        get_farmer_instance.first_name = validated_data['first_name']
        get_farmer_instance.last_name = validated_data['last_name']
        get_farmer_instance.birth_date = validated_data['birth_date']
        get_farmer_instance.phone = validated_data['phone']
        get_farmer_instance.address = validated_data['address']

        get_farmer_instance.save()
        return get_farmer_instance

class InvestorUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountInvestor
        fields = ['first_name', 'last_name', 'email','phone','address','city','zip_code','birth_date']

    
    def update(self, instance, validated_data):

        get_investor_instance = AccountInvestor.objects.get(
            user_uid = instance.user_uid
        )

        get_investor_instance.username = validated_data['first_name'].lower() + validated_data['last_name'].lower()
        get_investor_instance.first_name = validated_data['first_name']
        get_investor_instance.last_name = validated_data['last_name']
        get_investor_instance.email = validated_data['email']
        get_investor_instance.phone = validated_data['phone']
        get_investor_instance.address = validated_data['address']
        get_investor_instance.city = validated_data['city']
        get_investor_instance.zip_code = validated_data['zip_code']
        get_investor_instance.birth_date = validated_data['birth_date']

        get_investor_instance.save()
        return get_investor_instance

class AdminProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Owner
        fields = ['user_uid','username','email','profile']


    def to_representation(self,instance):
        data = super(AdminProfileSerializer, self).to_representation(instance)
        if data['profile'] is not None:
            data['profile'] = "https://bsgroup.org.in/" + data['profile']
        return data


class AdminProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Owner
        fields = ['username','profile']
        extra_kwargs = {
            'username':{"required":True},
            "profile":{"required":True},
            # "phone":{"required":True},
            # "address":{"required":True}
            # "email":{"required":True}
        }

    # def validate(self,attrs):
       
    #     regex_for_name = re.compile("^([A-Za-z])")

    #     first_name_regex = re.search(regex_for_name, attrs['first_name'])
    #     if not first_name_regex:
    #         raise serializers.ValidationError({"first_name": "first_name should contains only letters!"})

    #     last_name_regex = re.search(regex_for_name, attrs['last_name'])
    #     if not last_name_regex:
    #         raise serializers.ValidationError({"last_name": "last_name should contains only letters!"})

    #     address_regex = re.search(regex_for_name, attrs['address'])
    #     if not address_regex:
    #         raise serializers.ValidationError({"address": "address should contains only letters!"})
    
    #     if len(attrs['phone']) > 10 or len(attrs['phone']) < 10:
    #         raise serializers.ValidationError({"phone": "phone number is not valid!"})

    #     return attrs
    
    def update(self, instance, validated_data):
        
        get_profile_image = self.context.get("profile_image",None)

        instance.username = validated_data['username'] 
        # instance.first_name = validated_data['first_name']
        # instance.last_name =validated_data['last_name']
        # instance.phone = validated_data['phone']
        # instance.address = validated_data['address']
        #instance.email = validated_data['email']
        
        if get_profile_image is not None:
            instance.profile = get_profile_image

        instance.save()
        return instance