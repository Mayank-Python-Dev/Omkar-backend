from django.shortcuts import (
    get_object_or_404,
    get_list_or_404
)
from rest_framework import viewsets,generics
from rest_framework.response import Response
from rest_framework import status, exceptions,viewsets
from rest_framework.views import APIView
from account.models import (
    User,
    Rental
)
from service.models import (
    Service,
    SubService,
    ServiceRequest,
    Image,
    LeaveGalaRequest

)

from django.db.models.functions import Concat
from rest_framework_simplejwt.backends import TokenBackend
from warehouse.models import (
    Gala
)
from django.db.models import (
    Q,
    Value,
    CharField,
    Count,
    Case,When
)
from contract.models import (
    Contract,
    Investor as ContractInvestor,
    Rental as ContractRental
)
from warehouse.warehouse_api.serializers import (
    ContractRentalGalaSerializer
)

from contract.contract_api.serializers import (
    RentalPropertyFromContract
)

from service.service_api.serializers import (
    ServiceSerializer,
    SubServiceSerializer,
    SubServicePostSerializer,
    ServicesRequestSerializer,
    RentalNotificationSerializer,
    ServicesRequestStatusSerializer,
    ServiceAllRequestSerializer,
    LeaveGalaRequestSerializer,
    ViewContractSerializer
  
)
from django.shortcuts import get_object_or_404
from service.helpers import (
    ContractRentalFilter
)
import string
import random
from datetime import date,datetime,timedelta
from django.db.models import F

from fcm_django.models import FCMDevice
from django.shortcuts import get_object_or_404

from superadmin.firebaseManager import sendPush
from notification.models import (
    RentalNotification
)
from notification.notification_api.serializers import (
    RentalNotificationSerializer
)

from jwt_authentication.models import (
    TokenAuthentication
)

#in development server we need to add check_if_user_is_valid_or_not function to check is user is valid or not
# we have make this changes on production server


def check_if_user_is_valid_or_not(get_access_token,user_id):
    try:
        check_token = TokenAuthentication.objects.get(user=user_id)
        if check_token.access == get_access_token:
            return True
        else:
            return False
    except TokenAuthentication.DoesNotExist:
        return False




def get_context(serializer):
    context ={
            "status": status.HTTP_200_OK,
            "success": True,
            "response": serializer.data
    }
    return Response(context,status=status.HTTP_200_OK)

def get_exception_context(exception):
    context ={
            "status": status.HTTP_401_UNAUTHORIZED,
            "success": False,
            "response": str(exception)
    }
    return Response(context,status=status.HTTP_401_UNAUTHORIZED)

class ServiceListAPI(viewsets.ViewSet):
    authentication_classes = []
   
    def list(self, request):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            queryset = get_list_or_404(Service)
            serializer = ServiceSerializer(queryset,many=True)
            return get_context(serializer)
           
        except Exception as exception:
            return get_exception_context(exception)

    def create(self,request):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            serializer = ServiceSerializer(data= request.data)
            if serializer.is_valid():
                serializer.save()
                return get_context(serializer)
                
        except Exception as exception:
            return get_exception_context(exception)


class SubServiceListAPI(viewsets.ViewSet):
    authentication_classes = []

    def list(self,request):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            queryset = get_list_or_404(SubService)
            serializer = SubServiceSerializer(queryset,many=True)
            return get_context(serializer)
            
        except Exception as exception:
            return get_exception_context(exception)


    def create(self,request):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            serializer = SubServicePostSerializer(data = request.data)
            if serializer.is_valid():
                serializer.save()
                return get_context(serializer)

        except Exception as exception:
            return get_exception_context(exception) 


class ServiceRequestView(generics.CreateAPIView):
    authentication_classes = []
    serializer_class = ServicesRequestSerializer

    def get(self,request):
        try:
            # print(request.META['HTTP_HOST'])
            
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            # print(token)
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            get_user = Rental.objects.get(id=get_logged_in_user)
            flag = check_if_user_is_valid_or_not(token,get_logged_in_user)
            if not flag:
                print("Hello World!")
                context = {
                    'status':status.HTTP_401_UNAUTHORIZED,
                    'success':False,
                    'response':"Token is invalid or expired"
                } 
                return Response(context,status=status.HTTP_401_UNAUTHORIZED)

            service_type = self.request.query_params.get('service_type')
            # get_subservice_qs =list(SubService.objects.filter(service__service_name__iexact=service_type).values_list("sub_service_name",flat=True))
            get_subservice_qs = SubService.objects.filter(service__service_name__iexact=service_type)
            sub_service_serializer = SubServiceSerializer(get_subservice_qs,many=True)
            get_rental_gala = ContractRental.objects.filter(
                user_id=get_logged_in_user
                ).prefetch_related(
                    'gala__user_gala_leave_request'
                    ).values("gala__uid","gala__gala_number").annotate(
                        total_leave_request = Count("gala__user_gala_leave_request")
                    ).filter(total_leave_request = 0)

            context = {
                "status":status.HTTP_200_OK,
                "success":True,
                "response":{
                    "services":sub_service_serializer.data,
                    "rental-gala":get_rental_gala
                    }
            }
            return Response(context,status=status.HTTP_200_OK)

        except Exception as exception:
            context = {
                'status':status.HTTP_401_UNAUTHORIZED,
                'success':False,
                'response':str(exception)
            }
            return Response(context,status=status.HTTP_401_UNAUTHORIZED)

    
    def create(self, request,*args, **kwargs):
        
        try:  
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            flag = check_if_user_is_valid_or_not(token,get_logged_in_user)
            if not flag:
                print("Hello World!")
                context = {
                    'status':status.HTTP_401_UNAUTHORIZED,
                    'success':False,
                    'response':"Token is invalid or expired"
                } 
                return Response(context,status=status.HTTP_401_UNAUTHORIZED)
            get_user = User.objects.get(id=get_logged_in_user)
            get_sub_service_uid = request.POST.get('sub_service_uid')
            get_service_request_date = request.POST.get('service_date',datetime.strptime(str(datetime.today().date()),"%Y-%m-%d").strftime("%d-%m-%Y"))
            get_service_request_time = request.POST.get('service_time',datetime.strptime(str(datetime.today().time()),"%H:%M:%S.%f").strftime("%I:%M %p"))
            get_gala_uid=request.POST.get('gala_uid')
            get_upload_image=request.FILES.getlist('image')
            get_description=request.POST.get('description')
            print(get_service_request_date,get_service_request_time)
            get_service_request_date_and_time = get_service_request_date + " " + get_service_request_time
            
            get_service= SubService.objects.get(service_uid=get_sub_service_uid)
            get_contract_with_rental_instance = ContractRental.objects.filter(
                user_id=get_logged_in_user,
                gala__uid = get_gala_uid
                )
            
            get_gala_instance = Gala.objects.get(uid=get_gala_uid)
            check_service_request = ServiceRequest.objects.filter(
                Q(gala__uid=get_gala_uid)
                &Q(request_sub_service=get_service),
                status__in = ["Pending","In-progress","Accepted"]
                )

            if check_service_request:
                context = {
                    "status":status.HTTP_400_BAD_REQUEST,
                    "success":True,
                    "response":f"Request Already Submitted for {get_service}"
                }
                return Response(context,status=status.HTTP_400_BAD_REQUEST)
            elif get_contract_with_rental_instance.exists():
                get_gala_instance = Gala.objects.get(uid = get_gala_uid)
                request_instance = ServiceRequest.objects.create(
                    # tracking_id=tracking_id,
                    user_id = get_user.id,
                    request_sub_service=get_service,
                    gala=get_gala_instance,
                    service_request_date = datetime.strptime(get_service_request_date_and_time,"%d-%m-%Y %I:%M %p"),
                    description=get_description,
                )
                request_instance.save()

                if get_upload_image:
                    image_get_list = [
                        Image(
                            service_request_id = request_instance.id,
                            image = image
                        ) for image in get_upload_image
                    ]

                    Image.objects.bulk_create(image_get_list)
                
                try:
                    get_registration_token = get_object_or_404(FCMDevice,user=get_user)
                    sendPush("Gala Service Request",f"Your request has been submitted successfully! Your tracking id is {request_instance.tracking_id}",[get_registration_token.registration_id])
                    rental_notification = RentalNotification(
                        rental = get_user,
                        gala = get_gala_instance,
                        status = "Service_Gala",
                        sub_service_name = get_service.sub_service_name,
                        message = f"Your request has been submitted successfully for {get_service.sub_service_name} ! Your tracking id is {request_instance.tracking_id}"
                    )
                    rental_notification.save()
                    from asgiref.sync import async_to_sync
                    from channels.layers import get_channel_layer
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)('room_963',{'type': 'update_notification_instance',"text":"call-websocket"})
                except Exception as exception:
                    pass

                content = {
                    "status":status.HTTP_200_OK,
                    "success":True,
                    "response": f"Your request has been submitted successfully for {get_service.sub_service_name} ! Your tracking id is {request_instance.tracking_id}"
                    
                }  
                return Response(content,status=status.HTTP_200_OK)

            else:
                content = {
                    "status":status.HTTP_401_UNAUTHORIZED,
                    "sucess":False,
                    "response": "You don't have permission to request for this gala!" 

                }  
                return Response(content,status=status.HTTP_401_UNAUTHORIZED)
        except SubService.DoesNotExist as exception:
            context = {
                'status':status.HTTP_401_UNAUTHORIZED,
                'success':False,
                'response':"You have passed wrong sub service uid"
            }
            return Response(context,status=status.HTTP_401_UNAUTHORIZED)
        except Gala.DoesNotExist as exception:
            context = {
                'status':status.HTTP_401_UNAUTHORIZED,
                'success':False,
                'response':"You have passed wrong gala uid"
            }
            return Response(context,status=status.HTTP_401_UNAUTHORIZED)
        except Exception as exception:
            context = {
                'status':status.HTTP_401_UNAUTHORIZED,
                'success':False,
                'response':str(exception)
            }
            return Response(context,status=status.HTTP_401_UNAUTHORIZED)
    

    
class RentalServiceRequestStatus(APIView):
    authentication_classes = []
    
    def get(self,request,*args, **kwargs):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            # get_user = User.objects.get(id=get_logged_in_user)
                               
            # get_tracking_id=self.request.query_params.get('tracking_id')
            get_tracking_id=self.request.query_params.get('tracking_id')
            get_instance = ServiceRequest.objects.filter(
                tracking_id=get_tracking_id,
                user_id=get_logged_in_user
                ).values(
                    "tracking_id",
                    "user__username",
                    "request_sub_service__sub_service_name",
                    "gala__gala_number",
                    "service_request_date__date",
                    "service_request_date__time",
                    "description",
                    "status"
                    )
            if get_instance:
                # serializer = ServicesRequestStatusSerializer(get_instance)  
                context = {
                    "status":status.HTTP_200_OK,
                    "success":True,
                    "response":get_instance[0]
                }
                return Response(context,status=status.HTTP_200_OK)

            else:
                 context = {
                    "status":status.HTTP_400_BAD_REQUEST,
                    "success":True,
                    "response":"Enter The Valid Tracking Id"
                }
                 return Response(context,status=status.HTTP_401_UNAUTHORIZED)

        except Exception as exception:
            context = {
                'status':status.HTTP_401_UNAUTHORIZED,
                'success':False,
                'response':str(exception)
            }

            return Response(context,status=status.HTTP_401_UNAUTHORIZED)




    def post(self,request,*args, **kwargs):
        try: 

            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            # get_user = User.objects.get(id=get_logged_in_user)       

            get_tracking_id = request.data.get('tracking_id')
            get_instance = ServiceRequest.objects.get(tracking_id=get_tracking_id)
            if get_instance:
                get_instance.delete()
                context = {
                    "status":status.HTTP_200_OK,
                    "success":True,
                    "response":"Leave Request Successfully"
                }
                return Response(context,status=status.HTTP_200_OK)
            else:
                context = {
                    "status":status.HTTP_400_BAD_REQUEST,
                    "success":True,
                    "response":"Already Leave Request"
                }
                return Response(context,status=status.HTTP_400_BAD_REQUEST)
        except ServiceRequest.DoesNotExist:
            context = {
                'status':status.HTTP_400_BAD_REQUEST,
                'success':False,
                'response':"Leave Request is already removed as per your request!"
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)


        except Exception as exception:
            context = {
                'status':status.HTTP_401_UNAUTHORIZED,
                'success':False,
                'response':str(exception)
            }
            return Response(context,status=status.HTTP_401_UNAUTHORIZED)

class LeaveGalaRequestAPI(APIView):
    authentication_classes = []
    def post(self,request,*args, **kwargs):
        try: 
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            get_user = Rental.objects.get(id=get_logged_in_user) 
              
            get_gala_uid = request.data.get('gala_uid')
            get_description = request.data.get('description')
            get_gala_instance = Gala.objects.get(uid=get_gala_uid).id
            get_instance = ContractRental.objects.filter(gala=get_gala_instance)
            if LeaveGalaRequest.objects.filter(gala_id=get_gala_instance).exists():
                context = {
                    "status":status.HTTP_401_UNAUTHORIZED,
                    "success":True,
                    "response":f" Leave Request Already Submitted for {get_gala_instance} gala number "
                }
                return Response(context,status=status.HTTP_401_UNAUTHORIZED)
            elif get_instance:
                data=LeaveGalaRequest(user=get_user,gala_id=get_gala_instance,description= get_description)
                data.save()

                context = {
                    "status":status.HTTP_200_OK,
                    "success":True,
                    "response":"Leave Request Successfully"
                }
                return Response(context,status=status.HTTP_200_OK)
            
            else:
                context = {
                    "status":status.HTTP_400_BAD_REQUEST,
                    "success":True,
                    "response":"This gala does not belongs to you"
                }
                return Response(context,status=status.HTTP_400_BAD_REQUEST)

        except Exception as exception:
            context = {
                'status':status.HTTP_401_UNAUTHORIZED,
                'success':False,
                'response':str(exception)
            }
            return Response(context,status=status.HTTP_401_UNAUTHORIZED)


    def get(self,request,*args,**kwargs):

        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            get_user = Rental.objects.get(id=get_logged_in_user)

            get_instance = LeaveGalaRequest.objects.filter(id=get_user.id)
            serializer = LeaveGalaRequestSerializer(get_instance,many=True)
            context = {
                "status":status.HTTP_200_OK,
                "success":True,
                "response":serializer.data
            }
            return Response(context,status=status.HTTP_200_OK)

        except Exception as exception:
            context = {
                'status':status.HTTP_401_UNAUTHORIZED,
                'success':False,
                'response':str(exception)
            }
            return Response(context,status=status.HTTP_401_UNAUTHORIZED)


class RentalGetGalaAPI(APIView):
    authentication_classes = []
    def get(self, request,*args,**kwargs):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
          
            get_instance = ContractRental.objects.filter(user_id=get_logged_in_user).annotate(gala_detail=Concat( 'gala__gala_number',Value(' - '),'gala__warehouse__property_name', Value(' - '), 'gala__warehouse__company__name', output_field=CharField())).values('gala_detail')
        


            context = {
                "status":status.HTTP_200_OK,
                "success":True,
                "response":get_instance
           
            }
            return Response(context,status=status.HTTP_200_OK)

        except Exception as exception:
            context = {
                "status":status.HTTP_401_UNAUTHORIZED,
                "success":False,
                "response":str(exception)
            }
            return Response(context,status=status.HTTP_401_UNAUTHORIZED)    
            
            
class RentalAllServiceRequest(APIView):
    authentication_classes = []

    def get(self, request,*args,**kwargs):
        try:
            # token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            # valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            # get_logged_in_user = valid_data['user_id']
            get_user = User.objects.get(id=get_logged_in_user)
            get_instant = ServiceRequest.objects.filter(user_id=5).select_related("request_sub_service")
            serializer=ServiceAllRequestSerializer(get_instant,many=True,context = {"user_uid":get_user.user_uid})
            context = {
                "status":status.HTTP_200_OK,
                "success":True,
                "response":serializer.data
            }
            return Response(context,status=status.HTTP_200_OK)

        # except ServiceRequest.DoesNotExist:
        #     context = {
        #         "status":status.HTTP_401_UNAUTHORIZED,
        #         "success":False,
        #         "response":"As per your request, we are not able to find any request for your service!"
        #     }
        #     return Response(context,status=status.HTTP_401_UNAUTHORIZED)

        except Exception as exception:
            context = {
                "status":status.HTTP_401_UNAUTHORIZED,
                "success":False,
                "response":str(exception)
            }
            return Response(context,status=status.HTTP_401_UNAUTHORIZED)   


from django.db.models.functions import Concat
from django.db.models import CharField, Value,ExpressionWrapper,Func

class RentalGetServiceRequest(APIView):
    authentication_classes = []
    def get(self,request,user_uid,tracking_id):
        try:

            # token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            # valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            # get_logged_in_user = valid_data['user_id']
            # get_instance = ServiceRequest.objects.get(user__user_uid = user_uid,tracking_id = tracking_id).values(
            #         "tracking_id",
            #         "user__username",
            #         "service_request__sub_service_name",
            #         "gala__gala_number",
            #         "service_request_date__date",
            #         "service_request_date__time",
            #         "description",
            #         "status"
            #         )
            # print(request.build_absolute_uri())
            # query = DataTable.objects.annotate(C=)
            # .annotate(date_str=ExpressionWrapper(
            # Func(F('date'), Value('%d/%m/%Y %H:%i'), function='DATE_FORMAT'), output_field=CharField()
            #     ))
            get_instance = ServiceRequest.objects.filter(
                user__user_uid = user_uid,tracking_id = tracking_id
                ).values(
                    "tracking_id",
                    # "user__username",
                   
                    "service_request__sub_service_name",
                    "gala__gala_number",
                    "service_request_date__date",
                    "service_request_date__time",
                    "description",
                    "status",
                    # "get_service_date"
                    ).annotate(
                        username = Concat(F("user__first_name"), 
                        Value(' '), F("user__last_name"), output_field=CharField(),
                                         
                        )
                    ).annotate(
                        service_date=
                            Func(F('service_request_date__date'),
                            Value('%Y-%m-%d'),
                            function='DATE_FORMAT',
                            output_field=CharField())
                    )
            if get_instance:
                # serializer = ServicesRequestStatusSerializer(get_instance)
                context = {
                    "status":status.HTTP_200_OK,
                    "success":True,
                    "response":get_instance[0]
                }
                return Response(context,status=status.HTTP_200_OK)
            else:
                 context = {
                    "status":status.HTTP_401_UNAUTHORIZED,
                    "success":False,
                    "response":"Enter The Valid Tracking Id"
                }
                 return Response(context,status=status.HTTP_401_UNAUTHORIZED)

        except Exception as exception:
            context = {
                'status':status.HTTP_401_UNAUTHORIZED,
                'success':False,
                'response':str(exception)
            }
            return Response(context,status=status.HTTP_401_UNAUTHORIZED)




# class RentalProperties(APIView):
#     authentication_classes = []
#     def get(self, request,*args,**kwargs):
#         try:
#             # token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
#             # valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
#             # get_logged_in_user = valid_data['user_id']
#             # get_user = User.objects.get(id=get_logged_in_user)
#             # print()
           
#             # get_rental = ContractRental.objects.filter(
#             #     user_id=5).values(
#             #         "gala__warehouse__property_name",
#             #         "gala__warehouse__company__name",
#             #         "gala__gala_number",
#             #         "user__username",
#             #         "gala__warehouse__property_type",
#             #         "agreement_valid_doc"
#             #         )
#             get_rental = ContractRental.objects.filter(user_id=10).select_related("gala__warehouse__company","owner")
            
#             serializer = RentalPropertyFromContract(get_rental,many=True)
#             context = {
#                 "status":status.HTTP_200_OK,
#                 "success":True,
#                 "response":serializer.data
#             }
#             return Response(context,status=status.HTTP_200_OK)

#         except Exception as exception:
#             context = {
#                 "status":status.HTTP_401_UNAUTHORIZED,
#                 "success":False,
#                 "response":str(exception)
#             }
#             return Response(context,status=status.HTTP_401_UNAUTHORIZED)
class RentalProperties(APIView):
    authentication_classes = []
    def get(self, request,*args,**kwargs):
        try:
            # token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            # valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            # get_logged_in_user = valid_data['user_id']
            # get_user = User.objects.get(id=get_logged_in_user)
            # get_rental = ContractRental.objects.filter(
            #     user_id=get_user.id).values(
            #         "gala__warehouse__property_name",
            #         "gala__warehouse__company__name",
            #         "gala__gala_number",
            #         "user__username",
            #         "gala__warehouse__property_type",
            #         "agreement_valid_doc"
            #         )
            # print(request.build_absolute_uri())
            # get_rental = ContractRental.objects.filter(user_id=10).select_related("gala__warehouse__company","owner").annotate(
            #                                 request_count = Count("gala__gala_renew_request"),
            #                                 renew_status = F("gala__gala_renew_request__renew_status"),
            #                                 leave_request_count = Count("gala__user_gala_leave_request"),
            #                                 leave_request_status = F("gala__user_gala_leave_request__status")
            #                             )
            get_rental = ContractRental.objects.filter(user_id=10).select_related("gala__warehouse__company","owner").annotate(
                days=F('agreement_valid_end_date')-datetime.today().date(),
                request_count = Count("gala__gala_renew_request"),
                renew_status = F("gala__gala_renew_request__renew_status"),
                leave_request_count = Count("gala__user_gala_leave_request"),
                leave_request_status = F("gala__user_gala_leave_request__status")
            ).annotate(
                to_be_renewed = Case(
                When(
                    Q(days__lte = timedelta(days=90)) & Q(days__gte = timedelta(days=0)) | Q(days__lte = timedelta(days=0)) & Q(days__gte = timedelta(days=-30)),
                    leave_request_status = None,
                    renew_status = None,    
                    then = Value(True)),
                When(
                    Q(days__lte = timedelta(days=90)) & Q(days__gte = timedelta(days=0)) | Q(days__lte = timedelta(days=0)) & Q(days__gte = timedelta(days=-30)),
                    renew_status__in = ['Reject',None],
                    leave_request_status = "Pending",
                    then = Value(False)),
                When(
                    Q(days__lte = timedelta(days=90)) & Q(days__gte = timedelta(days=0)) | Q(days__lte = timedelta(days=0)) & Q(days__gte = timedelta(days=-30)),
                    renew_status = None,
                    leave_request_status = "Reject",
                    then = Value(True)),
                When(
                    Q(days__lte = timedelta(days=90)) & Q(days__gte = timedelta(days=0)) | Q(days__lte = timedelta(days=0)) & Q(days__gte = timedelta(days=-30)),
                    renew_status = "Pending",
                    leave_request_status = "Reject",
                    then = Value(False)),
                When(
                    Q(days__lte = timedelta(days=90)) & Q(days__gte = timedelta(days=0)) | Q(days__lte = timedelta(days=0)) & Q(days__gte = timedelta(days=-30)),
                    renew_status = "Reject",
                    leave_request_status = "Pending",
                    then = Value(False)),
                When(
                    Q(days__lte = timedelta(days=90)) & Q(days__gte = timedelta(days=0)) | Q(days__lte = timedelta(days=0)) & Q(days__gte = timedelta(days=-30)),
                    renew_status = "Reject",
                    leave_request_status = "Reject",
                    then = Value(True)),
                When(
                    Q(days__lte = timedelta(days=90)) & Q(days__gte = timedelta(days=0)) | Q(days__lte = timedelta(days=0)) & Q(days__gte = timedelta(days=-30)),
                    renew_status = "Reject",
                    leave_request_status = None,
                    then = Value(True)),
                default=False
                )
                
            )
            serializer = RentalPropertyFromContract(get_rental,many=True)
            context = {
                "status":status.HTTP_200_OK,
                "success":True,
                "response":serializer.data
            }
            return Response(context,status=status.HTTP_200_OK)

        except Exception as exception:
            context = {
                "status":status.HTTP_400_BAD_REQUEST,
                "success":False,
                "response":str(exception)
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)      

class RentalNotificationView(APIView):
    authentication_classes = []
    def get(self, request,*args,**kwargs):
        try:

            # token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            # valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            # get_logged_in_user = valid_data['user_id']
            get_rental_notification_instance = RentalNotification.objects.filter(rental_id = 5).order_by("-id")
            serializer = RentalNotificationSerializer(get_rental_notification_instance,many=True)
                
            context = {
                "status":status.HTTP_200_OK,
                "success":True,
                "response":serializer.data
            }
            return Response(context,status=status.HTTP_200_OK)

        except Exception as exception:
            context = {
                "status":status.HTTP_401_UNAUTHORIZED,
                "success":False,
                "response":str(exception)
            }
            return Response(context,status=status.HTTP_401_UNAUTHORIZED)  


class ViewContract(generics.ListAPIView):
    # model = ContractRental
    serializer_class = ViewContractSerializer
    # filter_class = ContractRentalFilter
    ordering_fields = (
        '-id',
    )
    def get_queryset(self):
        try:
            uuid = self.kwargs['uuid']
            user_type = self.request.query_params.get("user_type",'All')
            # print(user_type,651)
            if user_type == "All" or user_type == "":
                queryset = ContractRental.objects.filter(
                    user__user_uid=uuid
                    ).select_related(
                        'gala',
                        'owner',
                        'user'
                    )
            else:
                queryset = ContractRental.objects.filter(
                    user__user_uid=uuid,owner__groups__name__iexact = user_type
                    ).select_related(
                        'gala',
                        'owner',
                        'user'
                    )
            return queryset
        except Exception as exception:
            return None
    
    def get(self, request,uuid):
        try:
            # token = self.request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            # valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            # get_logged_in_user = valid_data['user_id']
            serializer = self.serializer_class(self.get_queryset(),many=True)
            context = {
                "status":status.HTTP_200_OK,
                "success":True,
                "response":serializer.data
            }
            return Response(context, status=status.HTTP_200_OK)
        except Exception as exception:
           context = {
            "status":status.HTTP_401_UNAUTHORIZED,
            "success":False,
            "response":str(exception)
           }
           return Response(context, status=status.HTTP_401_UNAUTHORIZED)

class ViewContractDetail(APIView):
    def get(self,request,uuid,*args,**kwargs):
        get_contract_obj = ContractRental.objects.filter(
            uid = uuid
        ).select_related(
            'gala',
            'owner',
            'user'
        )
        
        serializer = None
        pass


class GetGalaForLeaveRequest(APIView):
    def get(self, request,*args,**kwargs):
        try:
            # token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            # valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            # get_logged_in_user = valid_data['user_id']
            # ContractRental.objects.filter(user_id=5).prefetch_related('gala__user_gala_leave_request').values("gala__uid","gala__gala_number").annotate(total_leave_request = Count("gala__user_gala_leave_request")).filter(total_leave_request = 0)
            get_rental_gala = ContractRental.objects.filter(
                user_id=10,locking_period__lte=str(datetime.today().date())
                ).prefetch_related(
                    'gala__user_gala_leave_request'
                    ).values("gala__uid","gala__gala_number").annotate(
                        total_leave_request = Count("gala__user_gala_leave_request"),
                        leave_request_status  = F("gala__user_gala_leave_request__status"),
                        total_gala_renew_request = Count("gala__gala_renew_request")
                        
                    ).filter(Q(leave_request_status = None) | Q(leave_request_status = "Reject")).values("gala__uid","gala__gala_number","total_gala_renew_request").distinct().filter(total_gala_renew_request__lt=1)
            context = {
                "status":status.HTTP_200_OK,
                "success":True,
                "response":get_rental_gala
            }
            return Response(context,status=status.HTTP_200_OK)
        except Exception as exception:
            context = {
                'status':status.HTTP_400_BAD_REQUEST,
                'success':False,
                'response':str(exception)
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)
        
    def post(self,request,*args,**kwargs):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            get_gala_uid = request.POST.get('gala_uid')
            get_reason = request.POST.get('reason')
            get_gala_instance = Gala.objects.get(uid = get_gala_uid)
            check_existence = LeaveGalaRequest.objects.filter(
                user_id = get_logged_in_user,
                gala = get_gala_instance,
            ).exists()
            if check_existence:
                print(True)
                get_leave_request = LeaveGalaRequest.objects.get(
                    user_id = get_logged_in_user,
                    gala = get_gala_instance,
                )
                get_leave_request.reason_for_leaving = get_reason
                get_leave_request.status = "Pending"
                get_leave_request.save()
                get_registration_token = get_object_or_404(FCMDevice,user_id=get_logged_in_user)
                sendPush("Gala Leave Request",f"Your leave request has been submitted successfully!",[get_registration_token.registration_id])
            else:
                leave_request_obj = LeaveGalaRequest(
                    user_id = get_logged_in_user,
                    gala = get_gala_instance,
                    reason_for_leaving = get_reason
                )
                leave_request_obj.save()
                get_registration_token = get_object_or_404(FCMDevice,user_id=get_logged_in_user)
                sendPush("Gala Leave Request",f"Your leave request has been submitted successfully!",[get_registration_token.registration_id])
            context = {
                "status":status.HTTP_200_OK,
                "success":True,
                "response":"Your request is successfully submitted!"
            }
            return Response(context,status=status.HTTP_200_OK)

        except Exception as exception:
            context = {
                'status':status.HTTP_400_BAD_REQUEST,
                'success':False,
                'response':str(exception)
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST) 


class RenewRequestView(APIView):
    # authentication_classes = []
    def post(self, request,*args,**kwargs):
        try:
            # token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            # valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            # get_logged_in_user = valid_data['user_id']
            get_user_instance = AccountRental.objects.get(id=10)
            get_company_type = self.request.query_params.get('company_type')

            get_gala_uid = request.POST.get('gala_uid')
            
            get_gala_instance = Gala.objects.get(uid = get_gala_uid)
            get_rental_contract_gala_instance = ContractRental.objects.filter(
                                                                    user_id = get_user_instance,
                                                                    gala__uid = get_gala_uid,
                                                                    gala__warehouse__company__name__iexact=get_company_type
                                                                )
            # print(get_rental_contract_gala_instance,17)

            if RenewGalaRequest.objects.filter(renew_gala_id=get_gala_instance.id).exists():
                get_renew_request = RenewGalaRequest.objects.get(renew_gala_id=get_gala_instance.id)
                get_renew_request.renew_status = "Pending"
                get_renew_request.save()
                context = {
                    'status':status.HTTP_400_BAD_REQUEST,
                    'success':False,
                    "response":f"Request for Renewing your Contract for gala number {get_gala_instance.gala_number} has been Submitted Successfully!"
                    # "response":f"Request for Renewing your Contract for gala number {get_gala_instance.gala_number} has been Submitted Successfully!"
                    # 'response':f"Contract Renew Request for gala number {get_gala_instance.gala_number} has been Successfully Submitted and your request status is {get_renew_request.renew_status.lower()}!"
                }
                return Response(context,status=status.HTTP_400_BAD_REQUEST)

            elif get_rental_contract_gala_instance:
                renew_instance = RenewGalaRequest(renew_user_id = get_user_instance.id, renew_gala_id = get_gala_instance.id)
                renew_instance.save()

                try:
                    get_registration_token = get_object_or_404(FCMDevice,user=get_user_instance)
                    sendPush(
                        "Contract Renew Request",
                        f"Your request for contract renew has been submitted successfully for gala number {get_gala_instance.gala_number}!",
                        [get_registration_token.registration_id]
                    )
                    rental_notification = RentalNotification(
                        rental = get_user_instance,
                        gala = get_gala_instance,
                        status = "Renew_Request",
                        message = f"Your request for contract renew has been submitted successfully for gala number {get_gala_instance.gala_number} of  {get_gala_instance.warehouse}!"
                    )
                    rental_notification.save()
                    async_to_sync(channel_layer.group_send)(f"room_{get_gala_instance.warehouse.company.name}",{'type': 'update_notification_instance',"text":"call-websocket"})

                except Exception as exception:
                    pass

                context = {
                    'status':status.HTTP_200_OK,
                    'success':True,
                    'response':f"Request for Renewing your Contract for gala number {get_gala_instance.gala_number} has been Submitted Successfully!"
                }
                return Response(context , status=status.HTTP_200_OK)

            else:
                context = {
                    'status':status.HTTP_400_BAD_REQUEST,
                    'success':False,
                    'response':"This gala does not belongs to you!"
                }
                return Response(context , status=status.HTTP_400_BAD_REQUEST)

        except Exception as exception:
            context = {
                'status': status.HTTP_400_BAD_REQUEST,
                'success':False,
                'response': str(exception)
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)
