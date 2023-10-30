from rest_framework.views import APIView
from account.models import (
    Rental,
    Farmer,
    User,
)
from jwt_authentication.models import (
    TokenAuthentication
)
# from ipware import get_client_ip
from account.account_api.serializers import (
    RentalUserSerializer,
    FarmerUserSerializer,
    RentalUserPutSerializer,
    CutomTokenSerializer,

    ResetPasswordEmailSerializer,
    ResetPasswordSerializer,
    ChangePasswordSerializer,
    
)
from rest_framework.response import Response
from rest_framework_simplejwt.backends import TokenBackend
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse
from django.core.mail import send_mail
from rest_framework import generics

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.generics import RetrieveAPIView, CreateAPIView, GenericAPIView,UpdateAPIView
from rest_framework.permissions import IsAuthenticated


from rest_framework import (
    status
)
from rest_framework_simplejwt.backends import TokenBackend
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny
from account.models import (
    User
)
from account.account_api.serializers import (
    InvestorTokenSerializer,
    RentalTokenSerializer,
    get_token
)

from django.contrib.auth import authenticate
from fcm_django.models import FCMDevice
from rest_framework_simplejwt.views import TokenViewBase
from .serializers import (
    TokenRefreshLifetimeSerializer
)

class RentalLoginRefreshAPI(TokenViewBase):

    serializer_class = TokenRefreshLifetimeSerializer


def get_context(serializer):
    context = {
        "status":status.HTTP_201_CREATED,
        "success":True,
        "response":"Successfully Registered!"
    }
    return Response(context,status=status.HTTP_200_OK)

def get_exception_context(exception):
    context = {
        "status":status.HTTP_400_BAD_REQUEST,
        "success":False,
        "response":str(exception)
    }
    return Response(context,status=status.HTTP_400_BAD_REQUEST)

def get_else_condition_context(serializer):
    context= {
        "status":status.HTTP_400_BAD_REQUEST,
        "success":False,
        "response":serializer.errors
    }
    return Response(context,status=status.HTTP_400_BAD_REQUEST)

# @property
# def get_token_instance(self,request):
#     token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
#     valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
#     get_logged_in_user = valid_data['user_id']
#     get_user = User.objects.get(id=get_logged_in_user)
#     return get_user

class RentalRegistration(CreateAPIView):
    serializer_class = RentalUserSerializer
    def create(self, request):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                user = serializer.create(validated_data= serializer.validated_data)
                token = CutomTokenSerializer.get_token(user)
                context = {
                    "status":status.HTTP_201_CREATED,
                    "success":True,
                    "refresh":str(token),
                    "access":str(token.access_token),
                    "username":user.username,
                    "email":user.email,
                    "user_uid":user.user_uid
                }
                return Response(context,status=status.HTTP_201_CREATED)
            else:
                # print(serializers.errors.__dir__())
                # print(serializer_errors)
                serializer_errors = [value for key, value in serializer.errors.items()]
                # print(serializer_errors)
                context = {
                    "status":status.HTTP_400_BAD_REQUEST,
                    "success":False,
                    "response":serializer_errors[0][0]
                }
                return Response(context,status=status.HTTP_400_BAD_REQUEST)

        except Exception as exception:
            context = {
                "status":status.HTTP_400_BAD_REQUEST,
                "success":False,
                "response":str(exception)
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)

# class RentalRegistration(APIView):
#     def post(self, request, *args, **kwargs):
#         try:
#             data = request.data
#             serializer = RentalUserSerializer(data=data)
#             if serializer.is_valid():
#                 serializer.save()
#                 # token = CutomTokenSerializer.get_token(serializer)
#                 print(serializer.data)
#                 # context = {
#                 #     "status":status.HTTP_201_CREATED,
#                 #     "success":True,
#                 #     "refresh":str(token),
#                 #     "access":str(token.access_token),
#                 #     "username":user.username,
#                 #     "email":user.email
#                 # }
#                 context = {
#                     "status":status.HTTP_201_CREATED,
#                     "success":True,
#                     "response":serializer.data
#                 }
#                 return Response(context,status=status.HTTP_201_CREATED)
#             else:
#                 serializer_errors = {key: value[0] for key, value in serializer.errors.items()}
#                 context = {
#                     "status":status.HTTP_400_BAD_REQUEST,
#                     "success":False,
#                     "response":list(serializer_errors.values())[0]
#                 }
#                 return Response(context,status=status.HTTP_400_BAD_REQUEST)
#         except Exception as exception:
#             context = {
#                 "status":status.HTTP_400_BAD_REQUEST,
#                 "success":False,
#                 "response":str(exception)
#             }
#             return Response(context,status=status.HTTP_400_BAD_REQUEST)


class UserProfile(APIView):
    # authentication_classes = []
    def get(self,request):
        try:
            
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            get_user = User.objects.get(id=get_logged_in_user)

            # get_user=request.query_params.get('user_id')
            get_rental=Rental.objects.get(id=get_user.id)
            serialize = RentalUserPutSerializer(get_rental)
            context = {
                "status":status.HTTP_200_OK,
                "success":True,
                "response":serialize.data
            }
            return Response(context,status=status.HTTP_200_OK)
        
        except Exception as exception:
            context ={
                'status':status.HTTP_400_BAD_REQUEST,
                'success':False,
                'response':str(exception)
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)

    

    def put(self,request):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            # get_user = User.objects.get(id=get_logged_in_user)
            instance=Rental.objects.get(id=get_logged_in_user)
            print(instance)
            # data=request.data
            # get_rental.first_name = data['first_name']
            # get_rental.last_name = data['last_name']
            # get_rental.phone = data['phone']
            # get_rental.save()
            serializer = RentalUserPutSerializer(instance,data=request.data)
            if serializer.is_valid():
                serializer.save(username = request.data['first_name'] + ' ' + request.data['last_name'])
                context = {
                    "status":status.HTTP_200_OK,
                    "success":True,
                    "response":"Succesfully Updated!"
                }
                return Response(context,status=status.HTTP_200_OK)
            else:
                serializer_errors = {key: value[0] for key, value in serializer.errors.items()}
                context = {
                    "status":status.HTTP_400_BAD_REQUEST,
                    "success":False,
                    "response":serializer.errors
                }
                return Response(context,status=status.HTTP_400_BAD_REQUEST)
        except Exception as exception:
            context ={
                'status':status.HTTP_400_BAD_REQUEST,
                'success':False,
                'response':str(exception)
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)

class FarmerRegisteration(APIView):
    authentication_classes = []
    def post(self,request,*args,**kwargs):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            serializer = FarmerUserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return get_context(serializer)

            else:
                return get_else_condition_context(serializer)
        except Exception as exception:
            return get_exception_context(exception)


class PasswordReset(GenericAPIView):
    # authentication_classes = []
    serializer_class = ResetPasswordEmailSerializer
    def post(self, request):

        # token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        # valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
        # get_logged_in_user = valid_data['user_id']
        
       
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data["email"]
        user = User.objects.get(email=email)
        if user:
            encoded_pk = urlsafe_base64_encode(force_bytes(user.pk))
            token = PasswordResetTokenGenerator().make_token(user)
            reset_url = reverse("reset-password",kwargs={"encoded_pk": encoded_pk, "token": token},)
            base_url= request.build_absolute_uri('/')[:-1]
            
        
            reset_link = f"{base_url}{reset_url}"
            email_body =f"Your password reset link: {reset_link}"


            send_mail("Reset Your Omkar Development password",f"""Someone (hopefully you) has requested a password reset for your omkar development account.
             Follow the link to set a new password:{reset_link}""", 'kapilyadav@infograins.com', (user.email,),fail_silently=False)
            # send the rest_link as mail to the user.
            context = {
                "status":status.HTTP_200_OK,
                "success":f'We have sent you a link to {user.email} to  reset your password',
                "response":serializer.data,
                "link" :reset_link,
            }

            return Response(context,status=status.HTTP_200_OK)
        else:
            context = {
                "status":status.HTTP_400_BAD_REQUEST,
                "success":False,
                "message":"User doesn't exists"
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)



class ResetPasswordAPI(GenericAPIView):
    """
    Verify and Reset Password Token View.
    """

    serializer_class = ResetPasswordSerializer
	

    def patch(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data, context={"kwargs": kwargs})
            serializer.is_valid(raise_exception=True)
            context = {
                "status":status.HTTP_200_OK,
                "success":True,
                "message":"Password reset complete",
            }
            return Response(context,status=status.HTTP_200_OK)

        except Exception as exception:
            context = {
                "status":status.HTTP_400_BAD_REQUEST,
                "success":False,
                "response":serializer.errors
                
            }
        return Response(context,status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(UpdateAPIView):
    # authentication_classes = []
    serializer_class = ChangePasswordSerializer
    def update(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                context = {
                    "status":status.HTTP_200_OK,
                    "success":True,
                    "response":"Succesfully Updated!"
                }
                return Response(context,status=status.HTTP_200_OK)
            else:
                context = {
                    "status":status.HTTP_400_BAD_REQUEST,
                    "success":False,
                    "response":serializer.errors
                }
                return Response(context,status=status.HTTP_400_BAD_REQUEST)
        except Exception as exception:
            context ={
                'status':status.HTTP_400_BAD_REQUEST,
                'success':False,
                'response':str(exception)
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)



class InvestorLoginAPI(TokenObtainPairView):
    # permission_classes = (AllowAny,)
    serializer_class = InvestorTokenSerializer
  
class RentalLoginAPI(TokenObtainPairView):

    serializer_class = RentalTokenSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        email = data.get('email')
        password = data.get('password')
        # device_id = data.get('device_id')
        fcm_registration_token = data.get('fcm_registration_token',None)
        device_type = data.get('device_type',None)
        if fcm_registration_token is None:
            context = {
                "status":status.HTTP_400_BAD_REQUEST,
                "success":False,
                "erros_status":True,
                "response":"fcm_registration_token field may not be empty!"
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)
        if device_type is None:
            context = {
                "status":status.HTTP_400_BAD_REQUEST,
                "success":False,
                "erros_status":True,
                "response":"device_type field may not be empty!"
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)
        
        check_user_email = User.objects.filter(email__exact = email)
        if check_user_email.exists():
            user = authenticate(email = email, password = password)
            if user is not None:
                if user.groups.first().name == "Rental":
                    #check fcm device is exists or not
                    fcm_device_exists = FCMDevice.objects.filter(user_id=user.id).exists()
                    if fcm_device_exists:
                        # print(fcm_registration_token)
                        # print(json.loads(fcm_registration_token))
                        get_fcm_device = FCMDevice.objects.get(user_id=user.id)
                        get_fcm_device.registration_id = fcm_registration_token
                        get_fcm_device.type = device_type
                        get_fcm_device.active = True
                        get_fcm_device.save()
                    else:
                        fcm_instance = FCMDevice(
                        registration_id  = fcm_registration_token,
                        type  = device_type,
                        user_id = user.id,
                        # active = True
                        )
                        
                        # print(fcm_instance.__dir__())
                        fcm_instance.save()

                    token = self.get_serializer().get_token(user)
                    context = {
                        "status":status.HTTP_200_OK,
                        "success":True,
                        "erros_status":False,
                        "response":"Successfully Logged In!",
                        "refresh":str(token),
                        "access":str(token.access_token),
                        "username": user.username.title(),
                        "email":user.email,
                        "user_uid":user.user_uid
                    }
                    author, created = TokenAuthentication.objects.get_or_create(user_id = user.id,defaults={'access': context.get('access')})
                    if not created:
                        author.access = context['access']
                        author.save()
                    return Response(context,status=status.HTTP_200_OK)
                else:
                    context = {
                        "status":status.HTTP_401_UNAUTHORIZED,
                        "success":False,
                        "erros_status":True,
                        "response":"You are not authorized to access!"
                    }
                    return Response(context,status=status.HTTP_401_UNAUTHORIZED)
            else:
                context = {
                    "status":status.HTTP_400_BAD_REQUEST,
                    "success":False,
                    "erros_status":True,
                    "response":"Incorrect Password!"
                }
                return Response(context,status=status.HTTP_400_BAD_REQUEST)
        else:
            context = {
                "status":status.HTTP_400_BAD_REQUEST,
                "success":False,
                "erros_status":True,
                "response":"Please Enter valid email address!"
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)


        

