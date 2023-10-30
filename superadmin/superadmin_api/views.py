import namegenerator, random,calendar,pandas as pd
from django.contrib.auth.models import Group
from django.db import IntegrityError
from account.models import (
    User,
    Investor as AccountInvestor,
    Rental as AccountRental,
    Rental,
    Farmer,
    Farmer as AccountFarmer,
    Owner
)
from rest_framework_simplejwt.backends import TokenBackend
from account.account_api.serializers import (
    UserRentalSerializer,
    UserInvestorSerializer,
    InvestorUserSerializer,
    RentalWarehouseAndGalaSerializer,
    RentalWarehouseAndGalaDetailSerializer,
    FarmerListSerializer,
    AccountInvestorListSerializer,
    AccountRentalListSerializer,
    FarmerGalaDetailSerializer,
    InvestorListViewSerializer,
    TestFarmerListSerializer,
    TestFarmerListSerializer,
    InvestorListViewSerializer,
    FarmerUpdateSerializer,
    InvestorUpdateSerializer,
    AdminProfileSerializer,
    AdminProfileUpdateSerializer
    # InvestorDetailViewSerializer
)


from warehouse.models import (
    Company,
    Gala,
    Property,
    
)
from account.account_api.views import (
    get_context,
    get_exception_context,
    get_else_condition_context

)
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser
)
from django.contrib.auth import (
    authenticate,
    login,
    logout
)
from django.contrib.auth.models import Group
from rest_framework.decorators import api_view, permission_classes
from rest_framework import (
    status,
    viewsets
)
from django.shortcuts import (
    get_object_or_404,
    get_list_or_404
)
from superadmin.superadmin_api.serializers import (
    InvestorDetailSerializer,
    MyTokenObtainPairSerializer,
    RentalDetailSerializer,
    FarmerDetailSerializer,
    RemainingPropertySerializer,
)
from django.db.models import (
    Count,
    F,
    Sum,
    OuterRef,
    Value,
    IntegerField,
    Prefetch,
    Q,
    ExpressionWrapper,
    functions,
    CharField,
    Case,
    When
)

from rest_framework.generics import RetrieveAPIView, CreateAPIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.backends import TokenBackend

from employee.employee_api.serializers import (
    EmployeeSerializer
)

from employee.models import (
    Employee
)

from warehouse.warehouse_api.serializers import (
    CompanySerializer,
    PropertyDetailSerializer,
    GalaSerializer,
    RentalGalaSerializer,
    PropertySerializer,
    OwnerPropertySerializer,
    FarmerPropertySerializer,
    OwnerInvestorGalaSerializer,
    OwnerRentalGalaSerializer,
    OwnerRemainingGalaDetailSerializer,
    OwnerTotalRemainingGalaCountSerializer,
    LiveAndLicenseWarehouseSerializer,
    LiveAndLicensePropertyGalaSerializer,
    LiveAndLicenseDetailSerializer,
    PropertyPostSerializer,
    PropertyListSerializer,
    GalaPostSerializer,
    # RentalWarehouseAndGalaSerializer
    # TestPropertySerializer
    OwnerPropertyListSerializer,
    OwnerPropertyGalaListSerializer,

    PropertyGalaSerializer,
    GalaUpdateSerializer,
    DashboardViewSerializer,
    OwnerWarehouseListForFarmerSerializer,
    FarmerRemainingGalaDetailSerializer,
    InvestorRemainingGalaSerializer,
    InvestorRentalDetailSerializer,
    DashboardTotalGalaSerializer,
    DashboardTotalRemainingGalaSerializer,
    UpdatePropertySerializer


)

from contract.models import (
    Contract,
    Rental as ContractRental,
    Investor as ContractInvestor,
    Farmer as ContractFarmer
)
from contract.contract_api.serializers import (
    ContractSerializer,
    ContractInvestorSerializer,
    ContractRentalSerializer,
    CreateContractWithFarmer,
    # ContractInvestorPostSerializer,
    ContractInvestorPostSerializer,
    ContractWithRentalSerializer,
    FarmerRentalGalaDetailSerializer,
    InvestorRentalGalaDetailSerializer

)
from service.service_api.serializers import (
    ServicesRequestSerializer,
    ServiceSerializer,
    RenewGalaRequestSerializer,
)
from service.models import (
    ServiceRequest,
    Service ,
    SubService,
    RenewGalaRequest,
)

from rest_framework import viewsets
from django.core.exceptions import ValidationError
from rest_framework import generics



from warehouse.models import (
    PROPERTY_TYPE
)
from service.models import (
    ServiceRequest,
    LeaveGalaRequest
)
from service.service_api.serializers import (
    ServiceRequestSerializer,
    LeaveGalaRequestSerializer
)
from django_pandas.io import read_frame
from django.urls import reverse
import urllib

from superadmin.firebaseManager import sendPush
from fcm_django.models import FCMDevice
from django.shortcuts import get_object_or_404

from notification.models import (
    RentalNotification
)

from notification.notification_api.serializers import (
    DashboardRentalNotificationSerializer
)
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime,date
from dateutil.relativedelta import relativedelta
from django.db.models.functions import ExtractMonth, ExtractYear
from django_pandas.io import read_frame

def build_url(*args, **kwargs):
    get = kwargs.pop('get', {})
    url = reverse(*args, **kwargs)
    if get:
        url += '?' + urllib.parse.urlencode(get)
    return url


class TokenRefreshLifetimeSerializer(TokenRefreshSerializer):

    def validate(self, attrs):
        try:
            data = super().validate(attrs)
            refresh = RefreshToken(attrs['refresh'])
            print(refresh.access_token)
            print(refresh.__dir__())
            # print()
            # data['access_token'] = refresh['access_token']
            # data['lifetime'] = int(refresh.access_token.lifetime.total_seconds())
            user_instance = User.objects.get(id = refresh.payload['user_id'])
            return {
                "status":status.HTTP_200_OK,
                "error_status":False,
                "refresh":str(refresh),
                "access":str(refresh.access_token),
                "username":user_instance.username,
                "email":user_instance.email,
                "user_uid":user_instance.user_uid
            }
        except Exception as exception:
            return {
                'status':status.HTTP_401_UNAUTHORIZED,
                'error_status':True,
                'response':"You are not authorized to access",
                "exception":str(exception)
            }
        # return data

from rest_framework_simplejwt.views import TokenViewBase

class TokenRefreshView(TokenViewBase):
    """
        Renew tokens (access and refresh) with new expire time based on specific user's access token.
    """
    serializer_class = TokenRefreshLifetimeSerializer

class MyObtainTokenPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = MyTokenObtainPairSerializer


def check_bearer_token_is_valid_or_not(request):
    is_valid = False
    try:
        token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        valid_data = TokenBackend(
            algorithm='HS256').decode(token, verify=False)
        is_valid = True
        return is_valid
    except Exception as exception:
        return is_valid


class InvestorWarehousesView(APIView):
    authentication_classes = []

    def get(self, request, *args, **kwargs): 
        try:
            # token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            # valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            # get_logged_in_user = valid_data['user_id']
            get_company_type = self.request.query_params.get('company_type')
            get_warehouse_qs = Company.objects.get(
                name=get_company_type
            ).get_properties.filter(is_allotted_to_farmer=False).values(
                "uid", "property_name", "property_type", "property_survey_number", "address", "city", "state", "country"
            ).annotate(
                total_number_of_galas=Gala.objects.filter(
                                    warehouse__uid=OuterRef("uid"),
                                    is_allotted=True,
                                    
                                    warehouse__company__name__iexact=get_company_type
                                            ).values("warehouse__uid"
                                                    ).annotate(total_galas_allotted=Count("id")).values("total_galas_allotted"),

                total_number_of_investors=ContractInvestor.objects.filter(
                                    gala__warehouse__uid=OuterRef("uid"),
                                    gala__warehouse__company__name__iexact=get_company_type
                                            ).values("gala__warehouse__uid"
                                                    ).annotate(total_number_of_investors=Count("id")).values("total_number_of_investors")
            )
            serializer = PropertySerializer(get_warehouse_qs,
                                            many=True,
                                            context={
                                                "company_type": request.query_params.get("company_type")
                                            })
            context = {
                "status": status.HTTP_200_OK,
                "success": True,
                "response": serializer.data
            }
            return Response(context, status=status.HTTP_200_OK)
        except Exception as exception:
            context = {
                'status': status.HTTP_400_BAD_REQUEST,
                'success': False,
                'response': str(exception)
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)


class FarmerWarehousesView(APIView):
    # authentication_classes = []
    def get(self, request, *args, **kwargs):
        try:
            # token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            # valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            # get_logged_in_user = valid_data['user_id']

            # farmer_warehouse_detail__user__groups__name="Farmer"
            get_company_type = self.request.query_params.get('company_type')
            get_farmer_warehouses = Company.objects.get(name = get_company_type
                    ).get_properties.filter( is_allotted_to_farmer = True
                        ).values("uid","property_name", "property_type", "property_survey_number", "address", "city", "state", "country"
        ).annotate(
                total_number_of_galas = Gala.objects.filter(
                                                warehouse__uid=OuterRef("uid"),
                                                is_allotted_to_farmer=True,
                                                warehouse__company__name__iexact =get_company_type 
                                                    ).values("warehouse__uid"
                                                        ).annotate(total_number_of_galas =Count("id")).values("total_number_of_galas"),

                total_number_of_rentals=ContractRental.objects.filter(
                                                    gala__warehouse__uid=OuterRef("uid"),
                                                    owner__groups__name="Farmer",
                                                    gala__warehouse__company__name__iexact = get_company_type
                                                        ).values("gala__warehouse__uid"
                                                            ).annotate(total_number_of_rentals= Count("id")).values("total_number_of_rentals"),

                total_gala_allotted = Gala.objects.filter(
                                            warehouse__uid=OuterRef("uid"),
                                            is_allotted_to_farmer=True,
                                            gala_rental_contract_detail__owner__groups__name="Farmer",
                                            warehouse__company__name__iexact = get_company_type
                                                ).values("warehouse__uid"
                                                    ).annotate(total_gala_allotted=Count("id")).values("total_gala_allotted"),

                total_remaining_galas = Gala.objects.filter(
                                                warehouse__uid=OuterRef("uid"),
                                                is_allotted_to_farmer=True,
                                                is_allotted=False,
                                                is_allotted_to_rental=False,
                                                warehouse__company__name__iexact = get_company_type
                                                    ).values("warehouse__uid"
                                                        ).annotate(total_remaining_galas=Count("id")).values("total_remaining_galas"),

                farmer_name=ContractFarmer.objects.filter(warehouse__uid=OuterRef("uid"),warehouse__company__name__iexact = get_company_type).values("user__username"),
                farmer_uid=ContractFarmer.objects.filter(warehouse__uid=OuterRef("uid"),warehouse__company__name__iexact = get_company_type).values("user__user_uid")
                                                )
            serializer = FarmerPropertySerializer(get_farmer_warehouses, many=True, context={
                "company_type": request.query_params.get("company_type")
            })
            context = {
                "status": status.HTTP_200_OK,
                "success": True,
                "response": serializer.data
            }
            return Response(context, status=status.HTTP_200_OK)
        except Exception as exception:
            context = {
                'status': status.HTTP_400_BAD_REQUEST,
                'success': False,
                'response': str(exception)
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)


class FarmerRemainingGalaDetailView(APIView):
    # authentication_classes = []

    def get(self,request,uuid,*args,**kwargs):
        try:

            get_company_type = self.request.query_params.get("company_type")

            get_farmer_galas_qs = Company.objects.get(name__iexact=get_company_type).get_properties.get(uid= uuid
                                                ).get_gala.filter(
                                                    is_allotted_to_farmer=True,
                                                    is_allotted=False,
                                                    is_allotted_to_rental=False,
                                                    warehouse__company__name__iexact =get_company_type
                                                    )

            serializer = FarmerRemainingGalaDetailSerializer(get_farmer_galas_qs,many=True)
            context = {
                'status':status.HTTP_200_OK,
                'success':True,
                'response':serializer.data
            }
            return Response(context,status=status.HTTP_200_OK)


        except Exception as exception:
            context = {
                'status':status.HTTP_400_BAD_REQUEST,
                'success':False,
                'response':str(exception)
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)


""" had to make changes in this api / not in any use """
class RentalWarehousesView(APIView):
    authentication_classes = []
    def get(self, request, *args, **kwargs):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            get_company_type = self.request.query_params.get('company_type')
            get_warehouse_qs = Company.objects.get(
                name=get_company_type
            ).get_properties.all().values(
                "uid", "property_name", "property_type", "property_survey_number", "address", "city", "state", "country"
            ).annotate(
                total_number_of_galas=Gala.objects.filter(warehouse__uid=OuterRef("uid"), is_allotted=True).values(
                    "warehouse__uid").annotate(total_galas_allotted=Count("id")).values("total_galas_allotted"),
                total_number_of_investors=ContractRental.objects.filter(gala__warehouse__uid=OuterRef("uid")).values(
                    "gala__warehouse__uid").annotate(total_number_of_investors=Count("id")).values("total_number_of_investors")
            )
            serializer = PropertySerializer(get_warehouse_qs,
                                            many=True,
                                            context={
                                                "company_type": request.query_params.get("company_type")
                                            })
            context = {
                "status": status.HTTP_200_OK,
                "success": True,
                "response": serializer.data
            }
            return Response(context, status=status.HTTP_200_OK)
        except Exception as exception:
            context = {
                'status': status.HTTP_400_BAD_REQUEST,
                'success': False,
                'response': str(exception)
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)


class InvestorsGalaDetailView(APIView):
    authentication_classes = []
    def get(self, request, uuid, *args, **kwargs):
        try:
            # token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            # valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            # get_logged_in_user = valid_data['user_id']
            get_company_type = self.request.query_params.get('company_type')
            # get_investor_contracts_qs = ContractRental.objects.filter(
            #     gala__warehouse__uid = uuid,gala__warehouse__company__name  = get_company_type)
            # # print(get_investor_contracts_qs)
            # serializer = ContractRentalSerializer(get_investor_contracts_qs,many=True)
            # gala_rental_contract_detail__owner__groups__name="Investor"

            get_investor_contract_qs = Company.objects.get(
                name=get_company_type).get_properties.get(
                    uid=uuid).get_gala.filter(
                        is_allotted_to_farmer=False,
                        is_allotted = True,
                        warehouse__company__name__iexact = get_company_type,
                        gala_investor_contract_detail__user__groups__name="Investor"
            ).select_related(
                "gala_rental_contract_detail__owner", 
                "gala_rental_contract_detail__user",
                "gala_investor_contract_detail__owner",
                "gala_investor_contract_detail__user"
                )
            serializer = GalaSerializer(get_investor_contract_qs, many=True,context={"company_type":get_company_type})
            context = {
                "status": status.HTTP_200_OK,
                "success": True,
                "response": serializer.data
            }
            return Response(context, status=status.HTTP_200_OK)
        except Exception as exception:
            context = {
                'status': status.HTTP_400_BAD_REQUEST,
                'success': False,
                'response': str(exception)
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)


class FarmersGalaDetailViewAPI(APIView):
    authentication_classes = []
    def get(self, request, uuid,warehouse_uid,*args,**kwargs):
        try:
            get_company_type = self.request.query_params.get('company_type')
            
            get_farmer_obj = Farmer.objects.filter(
                user_uid = uuid,
                belong_to__name__iexact = get_company_type
                ).prefetch_related(
                    "get_investor_contract__gala",
                    "get_investor_contract__owner",
                    "get_investor_contract__user"
                )

            #     prefetch_related(
            #     Prefetch(
            #         "get_gala",
            #         queryset=Gala.objects.filter(is_allotted=False)
            #     )
            # )

            # print(get_farmer_obj)
            serializer = FarmerGalaDetailSerializer(get_farmer_obj,context={"warehouse_uid":warehouse_uid})
            context = {
                "status":status.HTTP_200_OK,
                "success":True,
                "response":serializer.data
            }
            return Response(context,status=status.HTTP_200_OK)
        except Exception as exception:
            context = {
                'status':status.HTTP_400_BAD_REQUEST,
                'success':False,
                'response':str(exception)
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)
    # def get(self, request, uuid, *args, **kwargs):
    #     try:
    #         token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
    #         valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
    #         get_logged_in_user = valid_data['user_id']
    #         get_company_type = self.request.query_params.get('company_type')
    #         # get_investor_contracts_qs = ContractRental.objects.filter(
    #         #     gala__warehouse__uid = uuid,gala__warehouse__company__name  = get_company_type)
    #         # # print(get_investor_contracts_qs)
    #         # serializer = ContractRentalSerializer(get_investor_contracts_qs,many=True)

    #         get_investor_contract_qs = Company.objects.get(
    #             name=get_company_type).get_properties.get(
    #                 uid=uuid).get_gala.filter(
    #                     gala_rental_contract_detail__owner__is_superuser=False
    #         ).select_related("gala_rental_contract_detail__owner", "gala_rental_contract_detail__user")
    #         serializer = GalaSerializer(get_investor_contract_qs, many=True)
    #         context = {
    #             "status": status.HTTP_200_OK,
    #             "success": True,
    #             "response": serializer.data
    #         }
    #         return Response(context, status=status.HTTP_200_OK)
    #     except Exception as exception:
    #         context = {
    #             'status': status.HTTP_400_BAD_REQUEST,
    #             'success': False,
    #             'response': str(exception)
    #         }
    #         return Response(context, status=status.HTTP_400_BAD_REQUEST)


class InvestorDetailView(APIView):
    authentication_classes = []
    def get(self, request, *args, **kwargs):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            check_project_type = self.request.query_params.get(
                "company_type", None)
            get_investors = Investor.objects.filter(
                belong_to__name__iexact=check_project_type)
            serializer = InvestorDetailSerializer(get_investors, many=True)
            context = {
                "status": status.HTTP_200_OK,
                "success": True,
                "response": serializer.data
            }
            return Response(context, status=status.HTTP_200_OK)
        except Exception as exception:
            context = {
                'status': status.HTTP_400_BAD_REQUEST,
                'success': False,
                'response': str(exception)
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)


class FarmerDetailView(APIView):
    authentication_classes = []
    def get(self, request, *args, **kwargs):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            check_project_type = self.request.query_params.get(
                "company_type", None)
            get_investors = Farmer.objects.filter(
                belong_to__name__iexact=check_project_type)
            serializer = FarmerDetailSerializer(get_investors, many=True)
            context = {
                "status": status.HTTP_200_OK,
                "success": True,
                "response": serializer.data
            }
            return Response(context, status=status.HTTP_200_OK)
        except Exception as exception:
            context = {
                'status': status.HTTP_400_BAD_REQUEST,
                'success': False,
                'response': str(exception)
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)


class RemainingPropertyView(APIView):
    authentication_classes = []
    def get(self, request, *args, **kwargs):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            check_project_type = self.request.query_params.get(
                "company_type", None)
            get_remaining_galas = Company.objects.get(name__iexact=check_project_type).get_properties.all().prefetch_related(
                Prefetch(
                    "get_gala",
                    queryset=Gala.objects.filter(is_allotted=False,warehouse__company__name__iexact = check_project_type)
                )
            )
            serializer = RemainingPropertySerializer(
                get_remaining_galas, many=True)
            context = {
                "status": status.HTTP_200_OK,
                "success": True,
                "response": serializer.data
            }
            return Response(context, status=status.HTTP_200_OK)
        except Exception as exception:
            return get_exception_context(exception)



class FarmerDetailView(APIView):
    authentication_classes = []
    def get(self, request, *args, **kwargs):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            check_project_type = self.request.query_params.get("company_type",None)
            get_investors = Farmer.objects.filter(belong_to__name__iexact = check_project_type)
            serializer = FarmerDetailSerializer(get_investors,many=True)
            context = {
                "status":status.HTTP_200_OK,
                "success":True,
                "response":serializer.data
            }
            return Response(context,status=status.HTTP_200_OK)
        except Exception as exception:
            context = {
                'status':status.HTTP_400_BAD_REQUEST,
                'success':False,
                'response':str(exception)
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)

class RemainingPropertyView(APIView):
    authentication_classes = []
    def get(self,request,*args,**kwargs):
        try:
            # token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            # valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            # get_logged_in_user = valid_data['user_id']
            check_project_type = self.request.query_params.get("company_type",None)
            get_remaining_galas = Company.objects.get(name__iexact=check_project_type).get_properties.all().prefetch_related(
                Prefetch(
                    "get_gala",
                    queryset = Gala.objects.filter(is_allotted = False)
                )
            )
            serializer = RemainingPropertySerializer(get_remaining_galas,many=True)
            context = {
                "status":status.HTTP_200_OK,
                "success":True,
                "response":serializer.data
            }
            return Response(context,status=status.HTTP_200_OK)
        except Exception as exception:
            return get_exception_context(exception)
# class RemainingPropertyView(APIView):
#     authentication_classes = []
#     def get(self,request,*args,**kwargs):
#         try:
#             token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
#             valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
#             get_logged_in_user = valid_data['user_id']
#             check_project_type = self.request.query_params.get("company_type",None)
#             get_remaining_galas = Company.objects.get(name__iexact=check_project_type).get_properties.all().prefetch_related(
#                 Prefetch(
#                     "get_gala",
#                     queryset = Gala.objects.filter(is_allotted = False)
#                 )
#             )
#             serializer = RemainingPropertySerializer(get_remaining_galas,many=True)
#             context = {
#                 "status":status.HTTP_200_OK,
#                 "success":True,
#                 "response":serializer.data
#             }
#             return Response(context,status=status.HTTP_200_OK)
#         except Exception as exception:
#             return get_exception_context(exception)


class RentalDetailView(APIView):
    authentication_classes = []
    def get(self, request, *args, **kwargs):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            check_project_type = self.request.query_params.get(
                "company_type", None)
            get_investors = Rental.objects.filter(
                belong_to__name__iexact=check_project_type)
            serializer = RentalDetailSerializer(get_investors, many=True)
            context = {
                "status": status.HTTP_200_OK,
                "success": True,
                "response": serializer.data
            }
            return Response(context, status=status.HTTP_200_OK)
        except Exception as exception:
            context = {
                'status': status.HTTP_400_BAD_REQUEST,
                'success': False,
                'response': str(exception)
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)


class EmployeeDetailView(APIView):
    authentication_classes = []
    def get(self, request, *args, **kwargs):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            get_employees = Employee.objects.all()
            serializer = EmployeeSerializer(get_employees, many=True)
            context = {
                "status": status.HTTP_200_OK,
                "success": True,
                "response": serializer.data
            }
            return Response(context, status=status.HTTP_200_OK)
        except Exception as exception:
            context = {
                'status': status.HTTP_400_BAD_REQUEST,
                'success': False,
                'response': str(exception)
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)


def fakedata():
    get_group = [1, 2]
    for _ in range(1, 51):
        user = User(
            username=namegenerator.gen(),
            app_type="android",
            # survey_number = uuid.uuid4().hex[:10]
        )
        user.email = user.username + "@gmail.com"
        user.set_password("Mayank@1412")
        user.save()
        user.groups.set([random.choice(get_group)])
        user.belong_to.set([random.choice(get_group)])
        user.save()


class CompanyAPI(viewsets.ModelViewSet):
    authentication_classes = []
    queryset = Company.objects.all().order_by("-id")
    serializer_class = CompanySerializer

    def list(self, request, *args, **kwargs):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            # fakedata()
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            context = {
                "status": status.HTTP_200_OK,
                "success": True,
                "response": serializer.data
            }
            return Response(context, status=status.HTTP_200_OK)
        except Exception as exception:
            context = {
                'status': status.HTTP_400_BAD_REQUEST,
                'success': False,
                'response': str(exception)
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)


class ContractInvestorDetailView(APIView):
    authentication_classes = []
    def get(self, request, uuid, *args, **kwargs):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            get_company_type = self.request.query_params.get("company_type")
            get_contract = Investor.objects.filter(user_uid=uuid,belong_to__name__iexact=get_company_type).prefetch_related(
                "investor_contract__gala__warehouse")
            # get_contract = Investor.objects.filter(user_uid=uuid)
            serializer = UserInvestorSerializer(get_contract, many=True)
            context = {
                "status": status.HTTP_200_OK,
                "success": True,
                "response": serializer.data
            }
            return Response(context, status=status.HTTP_200_OK)
        except Exception as exception:
            context = {
                'status': status.HTTP_400_BAD_REQUEST,
                'success': False,
                'response': str(exception)
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)


class ContractRentalDetailView(APIView):
    authentication_classes = []
    def get(self, request, uuid, *args, **kwargs):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            get_company_type = self.request.query_params.get("company_type")
            get_contract = Rental.objects.filter(user_uid=uuid,belong_to__name__iexact = get_company_type).prefetch_related(
                "rental_contract__gala__warehouse")
            serializer = UserRentalSerializer(get_contract, many=True)
            context = {
                "status": status.HTTP_200_OK,
                "success": True,
                "response": serializer.data
            }
            return Response(context, status=status.HTTP_200_OK)
        except Exception as exception:
            context = {
                'status': status.HTTP_400_BAD_REQUEST,
                'success': False,
                'response': str(exception)
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)


class PropertyDetailView(APIView):
    authentication_classes = []
    def get(self, request, *args, **kwargs):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            company_type = self.request.query_params.get('company_type', None)
            get_company_instance = get_object_or_404(
                Company, name__iexact=company_type)
            get_galas_detail = get_company_instance.get_properties.all().values(
                "uid", "company__name", "property_name"
            ).annotate(
                total_number_of_galas=Gala.objects.filter(
                                            warehouse__uid=OuterRef("uid"),
                                            warehouse__company__name__iexact = get_company_type
                                            ).values("warehouse__uid"
                                                ).annotate(total_galas_allotted=Count("id")).values("total_galas_allotted"),

                number_of_galas_is_allotted=Gala.objects.filter(
                                                warehouse__uid=OuterRef("uid"),
                                                is_allotted=True,
                                                warehouse__company__name__iexact = get_company_type
                                                ).values("warehouse__uid"
                                                    ).annotate(total_galas_allotted=Count("id")).values("total_galas_allotted"),

                remaining_number_of_galas=Gala.objects.filter(
                                                warehouse__uid=OuterRef("uid"),
                                                is_allotted=False,
                                                warehouse__company__name__iexact = get_company_type
                                                ).values("warehouse__uid"
                                                    ).annotate(total_galas_allotted=Count("id")).values("total_galas_allotted")
            )
            serializer = PropertyDetailSerializer(get_galas_detail, many=True)
            context = {
                "status": status.HTTP_200_OK,
                "success": True,
                "response": serializer.data
            }
            return Response(context, status=status.HTTP_200_OK)
        except Exception as exception:
            context = {
                'status': status.HTTP_400_BAD_REQUEST,
                'success': False,
                'response': str(exception)
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)


class LeaveAndLicenseDetailView(APIView):
    authentication_classes = []
    def get(self, request, uuid, *args, **kwargs):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            get_warehouse_detail = Property.objects.get(
                uid=uuid).get_gala.select_related("get_gala_detail")
            serializer = GalaSerializer(get_warehouse_detail, many=True)
            context = {
                "status": status.HTTP_200_OK,
                "success": True,
                "response": serializer.data
            }
            return Response(context, status=status.HTTP_200_OK)
        except Exception as exception:
            context = {
                'status': status.HTTP_400_BAD_REQUEST,
                'success': False,
                'response': str(exception)
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)


class OwnerWarehouseView(APIView):
    authentication_classes = []
    def get(self, request, *args, **kwargs):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
           
            get_company_type = self.request.query_params.get('company_type')
            get_owner_warehouse_queryset = Company.objects.get(name=get_company_type).get_properties.filter(
                Q(get_gala__gala_investor_contract_detail__owner__is_superuser=True) |
                Q(get_gala__gala_rental_contract_detail__owner__is_superuser=True),
            ).values("uid", "property_name", "property_type", "property_survey_number",
                     "address", "city", "state", "country").distinct().annotate(

                total_number_of_galas=Gala.objects.filter(
                                                warehouse__uid=OuterRef("uid"),
                                                warehouse__company__name__iexact=get_company_type
                                                          ).values('warehouse__uid'
                                                                   ).annotate(total_number_of_galas=Count("id")).values("total_number_of_galas"),

                total_number_of_investors=ContractInvestor.objects.filter(
                                                                gala__warehouse__uid=OuterRef("uid"), 
                                                                owner__is_superuser=True,
                                                                gala__warehouse__company__name__iexact=get_company_type
                                                                          ).values("gala__warehouse__uid"
                                                                                   ).annotate(total_number_of_investors=Count("id")).values("total_number_of_investors"),

                total_number_of_rentals=ContractRental.objects.filter(
                                                            gala__warehouse__uid=OuterRef("uid"),
                                                            owner__is_superuser=True,
                                                            gala__warehouse__company__name__iexact=get_company_type
                                                                      ).values("gala__warehouse__uid"
                                                                               ).annotate(total_number_of_rentals=Count("id")).values("total_number_of_rentals"),

                total_number_of_remaining_galas=Gala.objects.filter(
                                                        warehouse__uid=OuterRef("uid"),
                                                        is_allotted=False ,
                                                        is_allotted_to_rental=False,
                                                        is_allotted_to_farmer = False,
                                                        warehouse__company__name__iexact=get_company_type
                                                                    ).values('warehouse__uid'
                                                                             ).annotate(total_number_of_remaining_galas=Count("id")).values("total_number_of_remaining_galas"),

            )

            serializer = OwnerPropertySerializer(get_owner_warehouse_queryset, many=True,
                                                 context={
                                                     "company_type": request.query_params.get('company_type')
                                                 })
            context = {
                "status": status.HTTP_200_OK,
                "success": True,
                "response": serializer.data
            }
            return Response(context, status=status.HTTP_200_OK)

        except Exception as exception:
            context = {
                "status": status.HTTP_400_BAD_REQUEST,
                "success": False,
                "response": str(exception)
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)


class OwnerInvestorContractDetailView(APIView):
    authentication_classes = []
    def get(self, request, uuid, *args, **kwargs):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            get_company_type = self.request.query_params.get('company_type')
            # get_user_type = self.request.query_params.get('user_type')
            get_investor_gala_contract_detail = Company.objects.get(name__iexact=get_company_type

                                                                    ).get_properties.get(uid=uuid).get_gala.filter(

                gala_investor_contract_detail__owner__is_superuser=True,

            ).select_related("gala_investor_contract_detail__owner", "gala_investor_contract_detail__user")

            serializer = OwnerInvestorGalaSerializer(
                get_investor_gala_contract_detail, many=True)
            context = {
                "status": status.HTTP_200_OK,
                "success": True,
                "response": serializer.data
            }
            return Response(context, status=status.HTTP_200_OK)

        except Exception as exception:
            context = {
                "status": status.HTTP_400_BAD_REQUEST,
                "success": False,
                "response": str(exception)
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)


class OwnerRentalContractDetailView(APIView):
    authentication_classes =  []
    def get(self, request, uuid, *args, **kwargs):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            get_company_type = self.request.query_params.get('company_type')
            get_rental_contract_detail_w_owner = Company.objects.get(name__iexact=get_company_type
                                                                     ).get_properties.get(uid=uuid).get_gala.filter(

                gala_rental_contract_detail__owner__is_superuser=True,
                # gala_rental_contract_detail__user__groups__name__iexact = "Rental"
            ).select_related("gala_rental_contract_detail__owner", "gala_rental_contract_detail__user")

            serializer = OwnerRentalGalaSerializer(
                get_rental_contract_detail_w_owner, many=True)
            context = {
                "status": status.HTTP_200_OK,
                "success": True,
                "response": serializer.data
            }
            return Response(context, status=status.HTTP_200_OK)

        except Exception as exception:
            context = {
                "status": status.HTTP_400_BAD_REQUEST,
                "success": False,
                "response": str(exception)
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)


class OwnerRemainingGalaDetail(APIView):
    authentication_classes = []
    def get(self, request, uuid, *args, **kwargs):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            get_company_name = self.request.query_params.get("company_type")
            get_remaining_gala_queryset = Company.objects.get(name=get_company_name
                            ).get_properties.get(uid=uuid
                                ).get_gala.filter(is_allotted=False,is_allotted_to_farmer = False,is_allotted_to_rental=False)

            serializer = OwnerRemainingGalaDetailSerializer(get_remaining_gala_queryset,many=True)
            context = {
                "status": status.HTTP_200_OK,
                "success": True,
                "response": serializer.data
            }
            return Response(context, status=status.HTTP_200_OK)

        except Exception as exception:
            context = {
                "status": status.HTTP_400_BAD_REQUEST,
                "success": False,
                "response": str(exception)
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)


# class OwnerTotalRemainingGalaCount(APIView):
#     def get(self,request,*args,**kwargs):
#         try:
#             get_company_type = self.request.query_params.get("company_type")
#             # get_total_gala_count = Company.objects.get(name="Omkar").get_properties.all(
#             #     ).values("uid","property_name").annotate(
#             #         total_remaining_gala_count = Gala.objects.filter(warehouse__uid=OuterRef("uid"),is_allotted=False
#             #         ).values("warehouse__uid").annotate(total_remaining_gala_count = Count("id")).values("total_remaining_gala_count"))
#             get_total_gala_count = Company.objects.get(name="Omkar").get_properties.filter(get_gala__is_allotted=False).count()
#             serializer = OwnerTotalRemainingGalaCountSerializer(get_total_gala_count,many=True)

#             context = {
#                 "status":status.HTTP_200_OK,
#                 "success":True,
#                 "response":serializer.data
#             }
#             return Response(context,status=status.HTTP_200_OK)

#         except Exception as exception:
#             context = {
#                 "status":status.HTTP_400_BAD_REQUEST,
#                 "success":False,
#                 "response":str(exception)
#             }
#             return Response(context,status=status.HTTP_400_BAD_REQUEST)


class RentalGalaDetail(APIView):
    authentication_classes = []
    def get(self, request, *args, **kwargs):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            get_company_type = self.request.query_params.get("company_type")
            get_gala_instance = Gala.objects.filter(
                warehouse__company__name__iexact=get_company_type, is_allotted_to_rental=True).select_related("gala_rental_contract_detail__owner")
            # queryset = (
            #     Gala.objects.filter(warehouse__company__name="Omkar",is_allotted_to_rental=True)
            #     .prefetch_related(
            #         Prefetch(
            #             'gala_rental_contract_detail', to_attr='number_of_rentals',
            #             queryset=ContractRental.objects.all().annotate(
            #                 number_of_rentals = Count('id', distinct=True),
            #             )
            #         ),
            #     )
            # )

            serializer = RentalGalaSerializer(get_gala_instance, many=True)
            context = {
                "status": status.HTTP_200_OK,
                "success": True,
                "response": serializer.data
            }
            return Response(context, status=status.HTTP_200_OK)
        except Exception as exception:
            context = {
                "status": status.HTTP_400_BAD_REQUEST,
                "success": False,
                "response": str(exception)
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)

# 28-12-2022


class LiveAndLicenseWarehouseView(APIView):
    authentication_classes = []
    def get(self, request, *args, **kwargs):
        try:
            # token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            # valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            # get_logged_in_user = valid_data['user_id']
            get_company_name = self.request.query_params.get("company_type")
            # live_and_license_warehouse_qs = Company.objects.get(name=get_company_name).get_properties.all().values(
            #     "uid", "property_name", "city","is_allotted_to_farmer"
            #                                                                                               ).annotate(
            #     total_gala_count=Gala.objects.filter(warehouse__uid=OuterRef("uid")).values("warehouse__uid"
            #                                                                                 ).annotate(total_gala_count=Count("id")).values("total_gala_count"),
            #     total_allotted_galas=Gala.objects.filter(warehouse__uid=OuterRef("uid"), is_allotted=True).values("warehouse__uid"
            #                                                                                                       ).annotate(total_allotted_galas=Count("id")).values("total_allotted_galas"),
            #     total_remaining_galas=Gala.objects.filter(warehouse__uid=OuterRef("uid"), is_allotted=False,is_allotted_to_rental=False,is_allotted_to_farmer = False).values("warehouse__uid"
            #                                                                                                         ).annotate(total_remaining_galas=Count("id")).values("total_remaining_galas")
            # )
            live_and_license_warehouse_qs = Company.objects.get(
                name=get_company_name
            ).get_properties.all().values(
                "uid", "property_name", "city","is_allotted_to_farmer"
            ).annotate(
                total_gala_count = 
                Case(
                    When(
                        is_allotted_to_farmer = True,
                        then=Gala.objects.filter(
                            warehouse__uid=OuterRef("uid"),is_allotted_to_farmer=True,warehouse__company__name__iexact=get_company_name).values(
                            "warehouse__uid"
                    ).annotate(
                        total_gala_count=Count("id")).values(
                            "total_gala_count"
                    )),
                    When(
                        is_allotted_to_farmer = False,
                        then=Gala.objects.filter(
                            warehouse__uid=OuterRef("uid"),warehouse__company__name__iexact=get_company_name).values(
                            "warehouse__uid"
                    ).annotate(
                        total_gala_count=Count("id")).values(
                            "total_gala_count"
                    ))
                ),
                total_allotted_galas = Case(
                    When(
                        is_allotted_to_farmer = True,
                        then=Gala.objects.filter(
                            warehouse__uid=OuterRef("uid"),is_allotted_to_farmer=True,is_allotted_to_rental=True,warehouse__company__name__iexact=get_company_name).values(
                            "warehouse__uid"
                    ).annotate(
                        total_gala_count=Count("id")).values(
                            "total_gala_count"
                    )),
                    When(
                        is_allotted_to_farmer = False,
                        then=Gala.objects.filter(
                            warehouse__uid=OuterRef("uid"),is_allotted_to_rental=True,warehouse__company__name__iexact=get_company_name).values(
                            "warehouse__uid"
                    ).annotate(
                        total_gala_count=Count("id")).values(
                            "total_gala_count"
                    ))
                ),
                total_remaining_galas = Case(
                    When(
                        is_allotted_to_farmer = True,
                        then=Gala.objects.filter(
                            warehouse__uid=OuterRef("uid"),is_allotted_to_farmer=True,is_allotted_to_rental=False,warehouse__company__name__iexact=get_company_name).values(
                            "warehouse__uid"
                    ).annotate(
                        total_gala_count=Count("id")).values(
                            "total_gala_count"
                    )),
                    When(
                        is_allotted_to_farmer = False,
                        then=Gala.objects.filter(
                            warehouse__uid=OuterRef("uid"),is_allotted_to_rental=False,warehouse__company__name__iexact=get_company_name).values(
                            "warehouse__uid"
                    ).annotate(
                        total_gala_count=Count("id")).values(
                            "total_gala_count"
                    ))
                ),
                owner_type = Case(
                    When(
                        is_allotted_to_farmer = False,
                        then=Value(Owner.objects.first().username)),
                    When(
                        is_allotted_to_farmer = True,
                        then=ContractFarmer.objects.filter(warehouse__uid = OuterRef("uid"),warehouse__company__name__iexact=get_company_name).values("user__username")),output_field = CharField()
                    
                ),

            )
            serializer = LiveAndLicenseWarehouseSerializer(live_and_license_warehouse_qs, many=True, context={
                "company_type": request.query_params.get("company_type")
            })
            context = {
                "status": status.HTTP_200_OK,
                "success": True,
                "response": serializer.data
            }
            return Response(context, status=status.HTTP_200_OK)

        except Exception as exception:
            context = {
                "status": status.HTTP_400_BAD_REQUEST,
                "success": False,
                "response": str(exception)
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)


class LiveAndLicenseDetailView(APIView):
    authentication_classes = []
    def get(self, request, uuid, *args, **kwargs):
        # try:

        #     get_company_type = self.request.query_params.get("company_type")
        #     get_gala_qs = Company.objects.get(name=get_company_type).get_properties.get(uid=uuid
        #                                                                                 ).get_gala.select_related("gala_investor_contract_detail__user", "gala_rental_contract_detail__user")
        #     # get_property = Company.objects.get(name = get_company_type).get_properties.get(uid=uuid)
        #     print(get_gala_qs)

        #     serializer = LiveAndLicenseDetailSerializer(
        #         get_gala_qs,
        #         many=True,
        #         context={"company_type": self.request.query_params.get("company_type")})
        #     # # print(len(serializer.data))
        #     # serializer_data = serializer.data
        #     # warehouse_instance = LiveAndLicensePropertySerializer(Property.objects.get(uid=uuid)).data
        #     # serializer_data.insert(len(serializer.data)+1,{"warehouse": warehouse_instance})
        #     context = {
        #         "status": status.HTTP_200_OK,
        #         "success": True,
        #         "response": serializer.data
        #     }
        #     return Response(context, status=status.HTTP_200_OK)

        # except Exception as exception:
        #     context = {
        #         "status": status.HTTP_400_BAD_REQUEST,
        #         "success": False,
        #         "response": str(exception)
        #     }
        #     return Response(context, status=status.HTTP_400_BAD_REQUEST)
        try:
            # token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            # valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            # get_logged_in_user = valid_data['user_id']
            get_company_type = self.request.query_params.get("company_type")
            get_company_instance = Company.objects.get(
                name__iexact=get_company_type).get_properties.get(uid=uuid)
            # print(get_company_instance)
            serializer = LiveAndLicensePropertyGalaSerializer(get_company_instance)
            context = {
                "status": status.HTTP_200_OK,
                "success": True,
                "response": serializer.data
            }
            return Response(context, status=status.HTTP_200_OK)
        except Exception as exception:
            context = {
                "status": status.HTTP_400_BAD_REQUEST,
                "success": False,
                "response": str(exception)
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)


class RentalWarehouseAndGalaView(APIView):
    authentication_classes = []
    def get(self, request,*args, **kwargs):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            get_company_type = self.request.query_params.get("company_type")
            
            # total_number_of_warehouse = ContractRental.objects.filter(
            #         user_id = 5
            #     ).values(
            #     "gala__warehouse__id",
            #     "gala__warehouse__property_name"
            #     ).order_by("gala__warehouse__id").distinct().count()
        
            get_rental_qs = Rental.objects.filter(belong_to__name__iexact=get_company_type).values(
                "id","user_uid","username","first_name","last_name"
                ).annotate(
                    total_number_of_galas = ContractRental.objects.filter(user__user_uid = OuterRef("user_uid"),gala__warehouse__company__name__iexact=get_company_type).values(
                        'gala__warehouse_id').annotate(
                            gala_warehouse= Count("id",distinct=True)).values(
                                "gala_warehouse").annotate(
                                    total_number_of_galas=ExpressionWrapper(
                                            Count("id"),
                                            output_field=IntegerField()
                                        )).values(
                                'total_number_of_galas')
                ).annotate(
                    total_number_of_warehouse = ContractRental.objects.filter(user__user_uid = OuterRef("user_uid"),gala__warehouse__company__name__iexact=get_company_type).values(
                        'gala__warehouse_id'
                        ).annotate(
                            gala_warehouse = Count("gala__warehouse_id",distinct=True)).values(
                                "gala_warehouse").annotate(
                                    number_of_warehouse=ExpressionWrapper(
                                        Count("gala__warehouse_id",distinct=True),
                                        output_field=IntegerField()
                                    )
                                ).values('number_of_warehouse') 
                )

            
            #annotate(total_number_of_warehouse = Count(F("gala__warehouse_id"))).values("total_number_of_warehouse")
            # get_rental_qs = Rental.objects.filter(belong_to__name=get_company_type).values(
            #     "user_uid","username"
            # ).annotate(
            #     total_number_of_galas = ContractRental.objects.filter(
            #         user__user_uid = OuterRef("user_uid")
            #     ).values("user__user_uid").annotate(
            #         total_number_of_galas = Count("user__user_uid")
            #     ).values("total_number_of_galas"),
            # ).annotate(
            #     total_number_of_warehouse = Value(ContractRental.objects.filter(
            #         user_id = OuterRef("user_uid")
            #     ).values(
            #     "gala__warehouse__id",
            #     "gala__warehouse__property_name"
            #     ).order_by("gala__warehouse__id").distinct().count())
            # )
            serializer = RentalWarehouseAndGalaSerializer(get_rental_qs,many=True,context = {"company_type":get_company_type})
            context = {
                "status": status.HTTP_200_OK,
                "success": True,
                "response": serializer.data
            }
            return Response(context, status=status.HTTP_200_OK)
        except Exception as exception:
            context = {
                "status": status.HTTP_400_BAD_REQUEST,
                "success": False,
                "response": str(exception)
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)

class RentalWarehouseAndGalaDetailView(APIView):
    authentication_classes = []
    def get(self, request, uuid, *args, **kwargs):
        # try:
        #     get_company_type = self.request.query_params.get("company_type")
        #     get_rental_qs = Rental.objects.get(user_uid = uuid)
        #     serializer  = RentalWarehouseAndGalaDetailSerializer(get_rental_qs,context = {"company_type":get_company_type,"user_uid":uuid})
        #     context = {
        #         "status": status.HTTP_200_OK,
        #         "success": True,
        #         "response": serializer.data
        #     }
        #     return Response(context, status=status.HTTP_200_OK)
        # except Exception as exception:
        #     context = {
        #         "status": status.HTTP_400_BAD_REQUEST,
        #         "success": False,
        #         "response": str(exception)
        #     }
        #     return Response(context, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            get_company_type = self.request.query_params.get("company_type")
            get_rental_qs = Rental.objects.get(user_uid=uuid)
            serializer  = RentalWarehouseAndGalaDetailSerializer(get_rental_qs,context = {"company_type":get_company_type,"user_uid":uuid})
            context = {
                "status": status.HTTP_200_OK,
                "success": True,
                "response": serializer.data
            }
            return Response(context, status=status.HTTP_200_OK)
        except Exception as exception:
            context = {
                "status": status.HTTP_400_BAD_REQUEST,
                "success": False,
                "response": str(exception)
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)



#post api's 
#investor registration

class InvestorRegistration(APIView):
    authentication_classes = []
    def post(self, request, *args, **kwargs):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            data = request.data
            serializer = InvestorUserSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                context = {
                    "status":status.HTTP_200_OK,
                    "success":True,
                    "response":"Successfully Registered!"
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
            context = {
                "status":status.HTTP_400_BAD_REQUEST,
                "success":False,
                "response":str(exception)
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)


class OwnerGalaDetailView(APIView):
    def get(self,request,uuid,*args, **kwargs):

        pass

# 04 / 02 / 2023
class RentalsServiceRequestDetailView(APIView):
    # authentication_classes = []
    def get(self,request,*args, **kwargs):
        try:
            # token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            # valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            # get_logged_in_user = valid_data['user_id']
            get_company_type = self.request.query_params.get("company_type")
            get_service_type = self.request.query_params.get("service_type")
            get_instance =ServiceRequest.objects.filter(
                gala__warehouse__company__name__iexact = get_company_type,
                request_sub_service__service__service_name__iexact = get_service_type
                ).select_related(
                                "user",
                                "gala__warehouse",
                                "request_sub_service__service"
                                ).order_by("-id")

            serializer = ServicesRequestSerializer(get_instance,many=True)    
            context = {
                "status":status.HTTP_200_OK,
                "success":True,
                "response":serializer.data
            }
            return Response(context,status=status.HTTP_200_OK)

        except Exception as exception:
            context = {
                'status':status.HTTP_400_BAD_REQUEST,
                'success':False,
                'response':str(exception)
            }

            return Response(context,status=status.HTTP_400_BAD_REQUEST)



    
class AddPropertyView(generics.ListCreateAPIView):
    authentication_classes = []
    queryset = Property.objects.all()
    serializer_class = PropertyPostSerializer
    def create(self, request):
        token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
        get_logged_in_user = valid_data['user_id']
        serializer = PropertyPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            context = {
                "status":status.HTTP_201_CREATED,
                "success":True,
                "response": "Successfully Created!",
                "property_uid":serializer.data.get("uid")
            }
            return Response(context, status=status.HTTP_200_OK)
        else:
            serializer_errors = serializer.errors
            serializer_errors = {key: value[0] for key, value in serializer_errors.items()}
            context = {
                "status":status.HTTP_400_BAD_REQUEST,
                "success":False,
                "response": serializer_errors
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)


#For adding gala 
class PropertyListView(APIView):
    authentication_classes = []
    def get(self, request, *args, **kwargs):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            get_company_type = self.request.query_params.get("get_company_type",None)
            if get_company_type is not None:
                get_property_qs = Property.objects.filter(company__name__iexact = get_company_type).order_by("-id")
                # get_property_qs = Property.objects.filter(company__name = get_company_type).order_by("-id").values(
                #     "id","uid","company__name",
                #     "property_name","property_type",
                #     "property_survey_number","address",
                #     "city","zipcode","country","state",
                #     "is_allotted_to_farmer",
                #     "total_gala"
                #     )
                serializer = PropertyListSerializer(get_property_qs,many=True,context = {"company_type":get_company_type})
                context = {
                    "status":status.HTTP_200_OK,
                    "success":True,
                    "response": serializer.data
                }
                return Response(context, status=status.HTTP_200_OK)
            else:
                context = {
                    "status":status.HTTP_400_BAD_REQUEST,
                    "success":False,
                    "response":"you have to pass company_type"
                }
                return Response(context, status=status.HTTP_400_BAD_REQUEST)

        except Exception as exception:
            context = {
                "status":status.HTTP_400_BAD_REQUEST,
                "success":False,
                "response": str(exception)
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)

class AddGalaView(generics.CreateAPIView):
    authentication_classes = []
    queryset = Gala.objects.all()
    serializer_class = GalaPostSerializer

    def create(self, request):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            serializer = GalaPostSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                context = {
                    "status":status.HTTP_201_CREATED,
                    "success":True,
                    "response": "Successfully Created!"
                }
                return Response(context, status=status.HTTP_201_CREATED)
            else:
                serializer_errors = serializer.errors
                serializer_errors = {key: value[0] for key, value in serializer_errors.items()}
                context = {
                    "status":status.HTTP_400_BAD_REQUEST,
                    "success":False,
                    "response": serializer_errors
                }
                return Response(context, status=status.HTTP_400_BAD_REQUEST)
        except Exception as exception:
            context = {
                "status":status.HTTP_400_BAD_REQUEST,
                "success":False,
                "response": str(exception)
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
            
    
# get farmer first for adding contract with farmer
class FarmerListView(APIView):
    authentication_classes = []
    def get(self, request, *args, **kwargs):
        try:
            # token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            # valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            # get_logged_in_user = valid_data['user_id']
            get_company_type = self.request.query_params.get("company_type",None)
            if get_company_type is not None:
                get_farmer_qs = Farmer.objects.filter(belong_to__name__iexact = get_company_type).order_by("-id")

                serializer = FarmerListSerializer(get_farmer_qs,many=True)
                context = {
                    "status":status.HTTP_200_OK,
                    "success":True,
                    "response": serializer.data
                }
                return Response(context, status=status.HTTP_200_OK)
            else:
                context = {
                    "status":status.HTTP_400_BAD_REQUEST,
                    "success":False,
                    "response":"you have to pass company_type"
                }
                return Response(context, status=status.HTTP_400_BAD_REQUEST)

        except Exception as exception:
            context = {
                "status":status.HTTP_400_BAD_REQUEST,
                "success":False,
                "response": str(exception)
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)

class AddContractWithFarmerView(generics.CreateAPIView):
    authentication_classes = []
    queryset = ContractFarmer.objects.all()
    serializer_class = CreateContractWithFarmer

    def create(self, request):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            serializer = CreateContractWithFarmer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                context = {
                    "status":status.HTTP_201_CREATED,
                    "success":True,
                    "response": "Successfully Created!"
                }
                return Response(context, status=status.HTTP_200_OK)
        except Exception as exception:
            context = {
                "status":status.HTTP_400_BAD_REQUEST,
                "success":False,
                "response": str(exception)
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
    # def create(self, request, *args, **kwargs):
    #     try:
    #         data = {
    #             "company_uid": request.POST.get('company_uid', None),
    #             "property_name": request.POST.get('property_name', None),
    #             "property_type": request.POST.get('property_type', None),
    #             "property_survey_number":request.POST.get('property_survey_number', None),
    #             "address":request.POST.get('address',None),
    #             "city":request.POST.get('city',None),
    #             "zipcode":request.POST.get('zipcode',None),
    #             "country":request.POST.get('country',None), 
    #             "state":request.POST.get('state',None),
    #             }
    #         _serializer = self.serializer_class(data=data)  # NOQA
    #         if _serializer.is_valid(raise_exception=True):
    #             _serializer.save()
    #             context = {
    #                 "status":status.HTTP_201_CREATED,
    #                 "success":True,
    #                 "response": _serializer.data
    #             }
    #             return Response(context, status=status.HTTP_201_CREATED)
    #         else:
    #             print(serializers.errors) # NOQA
    #     except ValidationError as exception:
    #         context = {
    #             "status":status.HTTP_400_BAD_REQUEST,
    #             "success":False,
    #             "response": _serializer.errors
    #         }
    #         return Response(context, status=status.HTTP_400_BAD_REQUEST)  #



class InvestorListAPIView(generics.ListAPIView):
    authentication_classes = []
    serializer_class = AccountInvestorListSerializer
    
    def get(self,request,*args,**kwargs):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            get_company_type = self.request.query_params.get("company_type")
            queryset = AccountInvestor.objects.filter(belong_to__name__iexact = get_company_type).order_by("-id")
            serializer = self.get_serializer(queryset,many=True)
            context = {
                "status": status.HTTP_200_OK,
                "success":True,
                "response":serializer.data
            }
            return Response(context,status=status.HTTP_200_OK)
        
        except Exception as exception:
            context ={
                "status":status.HTTP_400_BAD_REQUEST,
                "success":False,
                "response":str(exception)
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)


# I DON'T KNOW WHAT AYAN WAS DOING WITH THIS API .. CATCH HIM AND PUT HIM IN JAIL HE IS CULPRIT
class RentalListAPI(generics.ListAPIView):
    authentication_classes = []
    serializer_class = AccountRentalListSerializer
    
    def get(self,request,*args,**kwargs):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            get_company_type = self.request.query_params.get("company_type")
            queryset = AccountRental.objects.filter(belong_to__name__iexact=get_company_type)
            serializer = self.get_serializer(queryset,many=True)
            context = {
                'status':status.HTTP_200_OK,
                'success':True,
                'response':serializer.data
            }
            return Response(context,status=status.HTTP_200_OK)

        except Exception as exception:
            context = {
                'status':status.HTTP_400_BAD_REQUEST,
                'success':False,
                'response':str(exception)
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)

class OwnerPropertyListAPI(viewsets.ViewSet):
    authentication_classes = []

    def list(self,request):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            get_company_type = self.request.query_params.get("company_type")
            # property_qs = Company.objects.get(name__iexact =get_company_type).get_properties.filter(is_allotted_to_farmer= False)
            property_qs = Property.objects.filter(
                company__name__iexact = get_company_type,
                is_allotted_to_farmer=False,
                get_gala__is_allotted = False,
                get_gala__is_allotted_to_rental = False,
                get_gala__is_allotted_to_farmer = False,
                ).order_by("-id").distinct()
            # property_qs = Property.objects.filter(
            #     company__name__iexact = get_company_type,
            #     is_allotted_to_farmer=False,
            # ).values("uid","property_name","is_allotted_to_farmer","get_gala__is_allotted","get_gala__is_allotted_to_rental","get_gala__is_allotted_to_farmer")
            serializer = OwnerPropertyListSerializer(property_qs,context = {"company_type":get_company_type},many=True)
            # df = read_frame(property_qs)
            # filter_df = (df['get_gala__is_allotted_to_rental'] == True) | (df['get_gala__is_allotted'] == True)
            # get_filtered_df = df.loc[filter_df]
            # result_df = df[~df['property_name'].isin(get_filtered_df['property_name'].unique())]
            # result_df = result_df.iloc[:,:2]
            # result_df["warehouse_gala"] = result_df['uid'].apply(lambda uid : build_url("get-owner-warehouse-galas",get={"company_type":"Omkar"},kwargs={"uuid":uid}))
            
    
            context = {
                'status':status.HTTP_200_OK,
                'success':True,
                'response':serializer.data
            }
            return Response(context,status=status.HTTP_200_OK)

        except Exception as exception:
            context = {
                'status':status.HTTP_400_BAD_REQUEST,
                'success':False,
                'response':str(exception)
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)


class OwnerPropertyListForFarmerAPI(viewsets.ViewSet):
    authentication_classes = []

    def list(self,request):
        try:
            # token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            # valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            # get_logged_in_user = valid_data['user_id']
            get_company_type = self.request.query_params.get("company_type")
            # property_qs = Company.objects.get(name__iexact =get_company_type).get_properties.filter(is_allotted_to_farmer= False)
            get_property = Property.objects.filter(
            company__name__iexact = "Omkar",is_allotted_to_farmer=False
            ).values("uid","property_name").annotate(
                total_galas = Gala.objects.filter(
                    Q(is_allotted = True)|Q(is_allotted_to_rental = True),
                    warehouse__uid=OuterRef("uid")).values("warehouse__uid").annotate(
                    total_galas=ExpressionWrapper(
                            Count("id"),
                            output_field=IntegerField(),
                        )
            ).values("total_galas")).annotate(
            total_number_of_galas = Gala.objects.filter(
                is_allotted = False,is_allotted_to_rental = False,
                warehouse__uid=OuterRef("uid")).values("warehouse__uid").annotate(
                total_number_of_galas=ExpressionWrapper(
                        functions.Coalesce(Count("id"),0),
                        output_field=IntegerField(),
                    )
        ).values("total_number_of_galas")).filter(total_galas__isnull = True,total_number_of_galas__gte = 1)
            # property_qs = Property.objects.filter(
            #     company__name__iexact = get_company_type,
            #     is_allotted_to_farmer=False,
            # ).values("uid","property_name","is_allotted_to_farmer","get_gala__is_allotted","get_gala__is_allotted_to_rental","get_gala__is_allotted_to_farmer")
            serializer = OwnerWarehouseListForFarmerSerializer(get_property,many=True,context = {"company_type":get_company_type})
            # df = read_frame(property_qs)
            # filter_df = (df['get_gala__is_allotted_to_rental'] == True) | (df['get_gala__is_allotted'] == True)
            # get_filtered_df = df.loc[filter_df]
            # result_df = df[~df['property_name'].isin(get_filtered_df['property_name'].unique())]
            # result_df = result_df.iloc[:,:2]
            # result_df["warehouse_gala"] = result_df['uid'].apply(lambda uid : build_url("get-owner-warehouse-galas",get={"company_type":"Omkar"},kwargs={"uuid":uid}))
            
    
            context = {
                'status':status.HTTP_200_OK,
                'success':True,
                'response':serializer.data
            }
            return Response(context,status=status.HTTP_200_OK)

        except Exception as exception:
            context = {
                'status':status.HTTP_400_BAD_REQUEST,
                'success':False,
                'response':str(exception)
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)

    
class OwnerPropertyGalaListAPI(generics.ListAPIView):
    authentication_classes = []
    serializer_class = OwnerPropertyGalaListSerializer
    def get(self,request,uuid,*args,**kwargs):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            get_company_type = self.request.query_params.get("company_type")
            gala_queryset = Company.objects.get(name__iexact = get_company_type).get_properties.get(uid=uuid
                                ).get_gala.filter(is_allotted=False,
                                                is_allotted_to_rental= False,
                                                is_allotted_to_farmer=False)

            
            serializer = self.get_serializer(gala_queryset,many=True)
            context ={
                'status':status.HTTP_200_OK,
                'success':True,
                'response':serializer.data
            }
            return Response(context,status=status.HTTP_200_OK)

        except Exception as exception:
            context = {
                'status':status.HTTP_400_BAD_REQUEST,
                'success':False,
                'response':str(exception)
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)
        

class ContractInvestorPostAPI(APIView):
    authentication_class = []
    def post(self,request,*args,**kwargs):
        try:
            # token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            # valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            # get_logged_in_user = valid_data['user_id']
            serializer = ContractInvestorPostSerializer(data = request.data)
            if serializer.is_valid():
                serializer.save()
                get_user = serializer.data.get("user")
                context = {
                    'status':status.HTTP_201_CREATED,
                    'success':True,
                    'response':f"Saledeed Contract Created Successfully with '{get_user}' "
                }
                return Response(context,status=status.HTTP_201_CREATED)
            else:
                serializer_errors = serializer.errors
                serializer_errors = {key: value[0] for key, value in serializer_errors.items()}
                context = {
                    "status":status.HTTP_400_BAD_REQUEST,
                    "success":False,
                    "response": serializer_errors
                }
                return Response(context, status=status.HTTP_400_BAD_REQUEST)


        except IntegrityError as exception:
                if 'UNIQUE constraint' in str(exception.args):
                    context = {
                        'status':status.HTTP_400_BAD_REQUEST,
                        'success':False,
                        'response':"You have already allotted!"
                    }
                    return Response(context,status=status.HTTP_400_BAD_REQUEST)

        except Exception as exception:
            if 'Token is invalid' in str(exception.args):
                context = {
                    'status':status.HTTP_401_UNAUTHORIZED,
                    'success':False,
                    'response':str(exception)
                }
                return Response(context,status=status.HTTP_401_UNAUTHORIZED)
            else:
                context = {
                    'status':status.HTTP_400_BAD_REQUEST,
                    'success':False,
                    'response':str(exception.message)
                }
                return Response(context,status=status.HTTP_400_BAD_REQUEST)


        

# for contract with rental only 

class GetUsersWithUserType(APIView):
    authentication_classes = []
    def get(self, request, *args, **kwargs):
        try:
            """ need to filter according to company_type """ """ passed company_type """
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            get_user_type = self.request.query_params.get('get_user_type',None)
            get_company_type = self.request.query_params.get('company_type',None)
            queryset = None
            if get_user_type is not None:
                if get_user_type == "Farmer":
                    # user__belong_to__name = get_company_type
                    queryset = ContractFarmer.objects.filter(user__groups__name = get_user_type).values("user__user_uid","user__username","user__email").distinct()
                    context = {
                        "status":status.HTTP_200_OK,
                        "success":True,
                        "response": queryset
                    }
                    return Response(context,status=status.HTTP_200_OK)
                elif get_user_type == "Investor":
                    queryset = ContractInvestor.objects.filter(user__groups__name = get_user_type).values("user__user_uid","user__username","user__email").distinct()
                    context = {
                        "status":status.HTTP_200_OK,
                        "success":True,
                        "response": queryset
                    }
                    return Response(context,status=status.HTTP_200_OK)
                elif get_user_type == "Owner":
                    queryset = Owner.objects.first()
                    context = {
                        "status":status.HTTP_200_OK,
                        "success":True,
                        "response": [{
                            "user__user_uid":queryset.user_uid,
                            "user__username":queryset.username,
                            "user__email":queryset.email
                        }]
                    }
                    return Response(context,status=status.HTTP_200_OK)
                else:
                    context = {
                        "status":status.HTTP_400_BAD_REQUEST,
                        "success":False,
                        "response":"you have to pass user_type"
                    }
                    return Response(context,status=status.HTTP_400_BAD_REQUEST)
        except Exception as exception:
            context = {
                "status":status.HTTP_400_BAD_REQUEST,
                "success":False,
                "response": str(exception)
                }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)
            

class GetGalaWithUserUUID(APIView):
    authentication_classes = []
    def get(self, request, uuid, *args, **kwargs):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            get_user_type = self.request.query_params.get('get_user_type',None)
            get_company_type = self.request.query_params.get("company_type")
            queryset = None
            if get_user_type is not None:
                if get_user_type == "Investor":
                    queryset = ContractInvestor.objects.filter(
                        user__user_uid = uuid,
                        gala__is_allotted = True,
                        gala__is_allotted_to_rental = False,
                        gala__warehouse__company__name=get_company_type
                    ).values(
                        "gala__uid","gala__warehouse__property_name"
                    ).annotate(
                        uid = F("gala__uid"),
                         gala__uid_with_warehouse=functions.Concat(
                            F('uid'), Value(f' -- '), F('gala__warehouse__property_name'), output_field=CharField())
                    ).values("gala__uid_with_warehouse","uid")
                    context = {
                        "status":status.HTTP_200_OK,
                        "success":True,
                        "response": queryset
                    }
                    return Response(context,status=status.HTTP_200_OK)
                elif get_user_type == "Farmer":
                    queryset_list = list(ContractFarmer.objects.filter(
                        user__user_uid = uuid,warehouse__company__name__iexact = get_company_type
                    ).values_list(
                        "warehouse",
                        flat = True
                    ))
                    queryset = Gala.objects.filter(
                        warehouse_id__in = queryset_list,
                        is_allotted_to_rental = False,
                        warehouse__company__name__iexact = get_company_type
                        ).values(
                            "uid","warehouse__property_name"
                        ).annotate(
                        gala__uid_with_warehouse=functions.Concat(
                            F('uid'), Value(f' -- '), F('warehouse__property_name'), output_field=CharField())
                        ).values(
                        "gala__uid_with_warehouse","uid"
                        )
                    context = {
                        "status":status.HTTP_200_OK,
                        "success":True,
                        "response": queryset
                    }
                    return Response(context,status=status.HTTP_200_OK)
                elif get_user_type == "Owner":
                    # queryset_list = list(ContractFarmer.objects.filter(
                    #     user__user_uid = uuid,
                    # ).values_list(
                    #     "warehouse",
                    #     flat = True
                    # ))
                    #need to pass company_type here when we get user type owner
                    queryset = Gala.objects.filter(
                        # warehouse_id__in = queryset_list,
                        is_allotted_to_rental = False,
                        is_allotted_to_farmer = False,
                        is_allotted = False,
                        warehouse__company__name__iexact = get_company_type
                        ).values(
                            "uid","warehouse__property_name"
                        ).annotate(
                        gala__uid_with_warehouse=functions.Concat(
                            F('uid'), Value(f' -- '), F('warehouse__property_name'), output_field=CharField())
                        ).values(
                        "gala__uid_with_warehouse","uid"
                        )
                    context = {
                        "status":status.HTTP_200_OK,
                        "success":True,
                        "response": queryset
                    }
                    return Response(context,status=status.HTTP_200_OK)
            
        except Exception as exception:
            context = {
                "status":status.HTTP_400_BAD_REQUEST,
                "success":False,
                "response": str(exception)
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)
            # except:
            #     print("Hello!")
            #     context = {
            #         'status':status.HTTP_400_BAD_REQUEST,
            #         'success':False,
            #         'response':str(exception)
            #     }
            #     return Response(context,status=status.HTTP_400_BAD_REQUEST)
                
            

class GetPropertyTypeView(APIView):
    authentication_classes = []
    def get(self, request,*args, **kwargs):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            get_property_type = [property_type[0] for property_type in PROPERTY_TYPE.choices]
            context = {
                "status":status.HTTP_200_OK,
                "success":True,
                "response":get_property_type
            }
            return Response(context,status=status.HTTP_200_OK)
        except Exception as exception:
            context = {
                'status':status.HTTP_400_BAD_REQUEST,
                'success':False,
                'response':str(exception)
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)


class GetGalaWithPropertyUID(APIView):
    authentication_classes = []
    def get(self, request, property_uid, *args,**kwargs):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            get_company_type = self.request.query_params.get("company_type")
            get_property_instance = Gala.objects.filter(warehouse__uid = property_uid,warehouse__company__name__iexact = get_company_type).values(
                "id","uid","gala_number",
                "gala_area_size","gala_price","is_allotted",
                "is_allotted_to_rental","is_allotted_to_farmer","warehouse__property_name"
            )
            # serializer = PropertyGalaSerializer(get_property_instance,many=True)
            context = {
                "status":status.HTTP_200_OK,
                "success":True,
                "response":get_property_instance
            }
            return Response(context,status=status.HTTP_200_OK)
        except Exception as exception:
            context = {
                'status':status.HTTP_400_BAD_REQUEST,
                'success':False,
                'response':str(exception)
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)

# class TestAPI(APIView):
    

#contract with rental 
class ContractWithRental(APIView):
    authentication_classes = []
    def post(self, request):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            serializer = ContractWithRentalSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                context = {
                    "status": status.HTTP_201_CREATED,
                    "success": True,
                    "response": "Contract Created With Rental!"
                }
                return Response(context,status=status.HTTP_201_CREATED)
            else:
                context = {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "success": True,
                    "response": serializer.errors
                }
                return Response(context,status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as exception:
            if 'UNIQUE constraint' in str(exception.args):
                context = {
                    'status':status.HTTP_400_BAD_REQUEST,
                    'success':False,
                    'response':"You have already allotted this gala!"
                }
                return Response(context,status=status.HTTP_400_BAD_REQUEST)
            else:
                context = {
                    'status':status.HTTP_400_BAD_REQUEST,
                    'success':False,
                    'response':exception.message
                }
                return Response(context,status=status.HTTP_400_BAD_REQUEST)


        # except Exception as exception:
        #     print(exception.__dir__())
        #     context = {
        #         'status':status.HTTP_400_BAD_REQUEST,
        #         'success':False,
        #         'response':str(exception)
        #     }
        #     return Response(context,status=status.HTTP_400_BAD_REQUEST)


class GalaUpdateView(APIView):
    authentication_classes = []
    def put(self,request,uuid):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']

            data = request.data
            get_gala_instance = Gala.objects.get(uid= uuid)
            # print(get_gala_instance)
            # get_warehouse_instance = Property.objects.get(uid = request.data.get("warehouse")).id
            serializer = GalaUpdateSerializer(get_gala_instance,data=data,partial=True)
            if serializer.is_valid():
                serializer.save()
                context = {
                    'status':status.HTTP_200_OK,
                    'success':True,
                    'response':serializer.data
                }
                return Response(context,status=status.HTTP_200_OK)
            
            else:
                context = {
                    'status':status.HTTP_400_BAD_REQUEST,
                    'response':serializer.errors
                }
                return Response(context,status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as exception:
            print(exception)

            
class GetRentalWithCompanyTypeAPI(APIView):
    authentication_classes = []
    def get(self, request,*args,**kwargs):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']

            get_company_type = self.request.query_params.get('company_type')
            get_rental_instance = Rental.objects.filter(
                groups__name = "Rental",
                belong_to__name__iexact = get_company_type
            ).values("user_uid","username","email")
            context = {
                "status": status.HTTP_200_OK,
                "success": True,
                "response": get_rental_instance
            }
            return Response(context,status=status.HTTP_200_OK)

        except Exception as exception:
            context = {
                'status':status.HTTP_400_BAD_REQUEST,
                'success':False,
                'response':str(exception)
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)


# class GalaUpdateView(generics.UpdateAPIView):
  
#     # parser_class = (FileUploadParser,)
#     # permission_classes = (AllowAny,)
#     queryset = Gala.objects.all()
#     serializer_class = GalaUpdateSerializer

#     def update(self, request, *args, **kwargs):
#         instance = self.get_object()
#         get_gala_uid_instance = Gala.objects.get(uid=request.data.get("gala")).id

#         instance.id = get_gala_uid_instance
#         instance.gala_number = request.data.get("gala_number")
#         instance.gala_area_size = request.data.get("gala_area_size")
#         instance.gala
#         instance.save()

#         serializer = self.get_serializer(instance, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         self.perform_update(serializer)
#         return Response(serializer.data)

        
# class FarmerListView(viewsets.ViewSet):
#     authentication_classes = []
#     serializer_class = FarmerListSerializer
#     # queryset = AccountFarmer.objects.all()

#     def list(self,request):
#         try:
#             token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
#             valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
#             get_logged_in_user = valid_data['user_id']

#             queryset = get_list_or_404(AccountFarmer)
#             serializer = self.get_serializer(queryset,many=True)
#             context = {
#                 'status':status.HTTP_200_OK,
#                 'success':True,
#                 'response':serializer.data
#             }
#             return Response(context,status=status.HTTP_200_OK)

#         except Exception as exception:
#             context = {
#                 'status':status.HTTP_400_BAD_REQUEST,
#                 'success':False,
#                 'response':str(exception)

#             }
#             return Response(context,status=status.HTTP_400_BAD_REQUEST)
            

""" currently not in use"""
class GetFarmerListViewAPI(APIView):
    authentication_classes = []
    def get(self,request,*args,**kwargs):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            get_company_type = self.request.query_params.get("company_type")
            # farmer_qs = Farmer.objects.filter(belong_to__name = "Omkar").values(
            #                             "email",
            #                             "user_uid",
            #                             "username",
            #                             "farmer_contract__user__username",
            #                             "farmer_contract__warehouse__property_name",
            #                             "farmer_contract__warehouse__company__name"
            #                             )
            # farmer_qs = Farmer.objects.filter(belong_to__name = "Omkar").annotate(
            #             warehouse_name = ContractFarmer.objects.filter(user__user_uid = OuterRef("user_uid")).values("warehouse__property_name"),
            #             warehouseUID = ContractFarmer.objects.filter(user__user_uid = OuterRef("user_uid")).values("warehouse__uid")
            #         ).annotate(
            #             gala_count = Gala.objects.filter(warehouse__uid = OuterRef("warehouseUID"),is_allotted_to_farmer=True).values("warehouse__uid"
            #                                         ).annotate(gala_count=Count("id")).values("gala_count"),
            #                     )

            farmer_qs = Farmer.objects.filter(belong_to__name = get_company_type).annotate(
                        warehouse_name = ContractFarmer.objects.filter(user__user_uid = OuterRef("user_uid")).values("warehouse__property_name"),
                        warehouseUID = ContractFarmer.objects.filter(user__user_uid = OuterRef("user_uid")).values("warehouse__uid")
                    ).annotate(
                        total_gala_count = Gala.objects.filter(warehouse__uid = OuterRef("warehouseUID"),is_allotted_to_farmer=True
                                                            ).values("warehouse__uid").annotate(gala_count=Count("id")
                                                                                                            ).values("gala_count"),
                        remaining_gala_count = Gala.objects.filter(warehouse__uid=OuterRef("warehouseUID"),
                                                                   is_allotted_to_farmer=True,
                                                                   is_allotted=False,
                                                                   is_allotted_to_rental=False
                                                                    ).values("warehouse__uid").annotate(remaining_gala_count=Count("id")
                                                                                                                                ).values("remaining_gala_count"),
                        allotted_gala_count = Gala.objects.filter(warehouse__uid=OuterRef("warehouseUID"),
                                                                  is_allotted_to_farmer=True,
                                                                  is_allotted_to_rental=True,
                                                                  is_allotted=False
                                                                    ).values("warehouse__uid"
                                                                         ).annotate(allotted_gala_count=Count("id")
                                                                                                            ).values("allotted_gala_count")
                                )

            serializer = TestFarmerListSerializer(farmer_qs,many=True,context = {"company_type":get_company_type})
            context = {
                'status':status.HTTP_200_OK,
                'success':True,
                'response':serializer.data
            }
            return Response(context,status=status.HTTP_200_OK)
        except Exception as exception:
            context = {
                'status':status.HTTP_400_BAD_REQUEST,
                'success':False,
                'response':str(exception)
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)


# class FarmerPropertyView(APIView):
#     def get(self,request,uuid,*args,**kwargs):
#         try:
#             get_company_type = self.request.query_params.get("company_type")
#             farmer_property_qs = ContractFarmer.objects.filter(user__user_uid = "5f82381f-d95b-4cff-b2b8-0077c6d1f104"
#                                     ).values("warehouse__uid")

#             pass

#         except Exception as exception:
#             pass              







class PropertyUpdateView(APIView):
    def put(self,request,*args,**kwargs):
        pass


class ContractRentalUpdateView(APIView):
    def put(self,request,*args,**kwargs):
        pass


class ContractInvestorUpdateView(APIView):
    def put(self,request,*args,**Kwargs):
        pass


class FarmerGalaDetailView(APIView):
    authentication_classes = []
    def get(self,request,uuid,*args,**kwargs):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            get_company_type = self.request.query_params.get("company_type")

            get_contract_rental = ContractRental.objects.filter(uid=uuid,gala__warehouse__company__name__iexact=get_company_type).select_related("gala__warehouse__company","owner","user")
            serializer = FarmerRentalGalaDetailSerializer(get_contract_rental,many=True)
            context = {
                "status": status.HTTP_200_OK,
                "success": True,
                "response": serializer.data[0]
            }
            return Response(context,status=status.HTTP_200_OK)
        except Exception as exception:
            context = {
                "status":status.HTTP_400_BAD_REQUEST,
                "success":False,
                "response":str(exception)
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)
        
class InvestorListView(APIView):
    authentication_classes = []
    def get(self, request, *args, **kwargs):
        try:
            # token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            # valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            # get_logged_in_user = valid_data['user_id']
            get_company_type = self.request.query_params.get('company_type')
            get_investor_instance = AccountInvestor.objects.filter(belong_to__name = get_company_type).values(
                "id","user_uid","username","first_name","last_name","address","phone","address",
                "city","zip_code","belong_to__name"
                ).annotate(
                    total_galas = ContractInvestor.objects.filter(
                                        user__user_uid = OuterRef("user_uid"),
                                        gala__is_allotted=True,
                                        gala__warehouse__company__name__iexact=get_company_type).values(
                                            "user__user_uid"
                                                    ).annotate(total_galas=Count("id")).values("total_galas"),

                    total_rentals = ContractRental.objects.filter(
                                        owner__user_uid = OuterRef("user_uid"),
                                        gala__is_allotted_to_rental=True,
                                        gala__is_allotted_to_farmer = False,
                                        gala__warehouse__company__name__iexact=get_company_type).values(
                                            "user__user_uid"
                                                    ).annotate(total_rentals=Count("id")).values("total_rentals"),

                    total_remaining_galas = ContractInvestor.objects.filter(
                                        user__user_uid = OuterRef("user_uid"),
                                        gala__is_allotted_to_rental=False,
                                        gala__is_allotted_to_farmer=False,
                                        gala__warehouse__company__name__iexact=get_company_type).values(
                                                            "user__user_uid"
                                                                    ).annotate(total_remaining_galas = Count("id")).values("total_remaining_galas"),

                    # warehouseUID = ContractInvestor.objects.filter(user__user_uid = OuterRef("user_uid")).values("gala__warehouse__uid")

                    ).order_by("-id")

            # serializer path = account/account_api/serializer
            serializer = InvestorListViewSerializer(get_investor_instance,many=True,context= {"company_type":get_company_type})
            # serializer = InvestorListViewSerializer(get_investor_instance,many=True)
            context = {
                "status": status.HTTP_200_OK,
                "success": True,
                "response": serializer.data
            }
            return Response(context,status=status.HTTP_200_OK)
        except Exception as exception:
            context = {
                "status":status.HTTP_400_BAD_REQUEST,
                "success":False,
                "response":str(exception)
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)

class InvestorGalaDetailView(APIView):
    pass
# for investor list view       
class InvestorListView(APIView):
    authentication_classes = []
    def get(self, request, *args, **kwargs):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            get_company_type = self.request.query_params.get('company_type')
            get_investor_instance = AccountInvestor.objects.filter(belong_to__name = get_company_type).values(
                "id","user_uid","username","first_name","last_name","email","birth_date","address","phone","address",
                "city","zip_code","belong_to__name"
                ).annotate(
                    total_galas = ContractInvestor.objects.filter(
                                        user__user_uid = OuterRef("user_uid"),
                                        gala__is_allotted=True,
                                        gala__warehouse__company__name__iexact=get_company_type).values(
                                            "user__user_uid"
                                                    ).annotate(total_galas=Count("id")).values("total_galas"),

                    total_rentals = ContractRental.objects.filter(
                                        owner__user_uid = OuterRef("user_uid"),
                                        gala__is_allotted_to_rental=True,
                                        gala__is_allotted_to_farmer = False,
                                        gala__warehouse__company__name__iexact=get_company_type).values(
                                            "user__user_uid"
                                                    ).annotate(total_rentals=Count("id")).values("total_rentals"),

                    total_remaining_galas = ContractInvestor.objects.filter(
                                        user__user_uid = OuterRef("user_uid"),
                                        gala__is_allotted_to_rental=False,
                                        gala__is_allotted_to_farmer=False,
                                        gala__warehouse__company__name__iexact=get_company_type).values(
                                                            "user__user_uid"
                                                                    ).annotate(total_remaining_galas = Count("id")).values("total_remaining_galas"),

                    # warehouseUID = ContractInvestor.objects.filter(user__user_uid = OuterRef("user_uid")).values("gala__warehouse__uid")

                    ).order_by("-id")
            # print(ContractInvestor.objects.all().values("gala__uid"))
            # serializer path = account/account_api/serializer
            serializer = InvestorListViewSerializer(get_investor_instance,many=True,context= {"company_type":get_company_type})
            context = {
                "status": status.HTTP_200_OK,
                "success": True,
                "response": serializer.data
            }
            return Response(context,status=status.HTTP_200_OK)
        except Exception as exception:
            context = {
                "status":status.HTTP_400_BAD_REQUEST,
                "success":False,
                "response":str(exception)
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)

# for investor list view
class InvestorRemainingGalaView(APIView):
    # authentication_classes = []
    def get(self,request,uuid,*args,**kwargs):
        try:
            # token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            # valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            # get_logged_in_user = valid_data['user_id']
            get_company_type = self.request.query_params.get("company_type")
            investor_qs = ContractInvestor.objects.filter(
                                            user__user_uid = uuid,
                                            gala__warehouse__company__name__iexact=get_company_type, 
                                            gala__is_allotted_to_rental = False,
                                            gala__is_allotted_to_farmer=False).select_related(
                                                                                "gala__warehouse"
                                                                                )

            # serializer path = warehouse/warehouse_api/serializer
            serializer = InvestorRemainingGalaSerializer(investor_qs,many=True)
            context = {
                'status':status.HTTP_200_OK,
                'success':True,
                'response':serializer.data
            }
            return Response(context,status=status.HTTP_200_OK)

        except Exception as exception:
            context ={
                'status':status.HTTP_400_BAD_REQUEST,
                'success':False,
                'response':str(exception)
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)

class InvestorRentalDetailView(APIView):
    # authentication_classes = []
    def get(self,request,uuid,*args,**kwargs):
        try:
            # token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            # valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            # get_logged_in_user = valid_data['user_id']
            get_company_type = self.request.query_params.get("company_type")
            rental_qs = ContractRental.objects.filter(owner__user_uid= uuid,gala__warehouse__company__name__iexact = get_company_type).select_related(
                "gala__warehouse",
                "owner",
                "user"
            )
            serializer = InvestorRentalDetailSerializer(rental_qs,many=True)
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

            
# same as above but getting gala_uid instead of owner__user_uid 
class InvestorGalaDetailView(APIView):
    # authentication_classes = []
    def get(self, request, uuid, *args, **kwargs):
        try:
            # token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            # valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            # get_logged_in_user = valid_data['user_id']
            get_contract_rental = ContractRental.objects.filter(
                gala__uid=uuid
                ).select_related("gala__warehouse__company","owner","user")
            # print(get_contract_rental)

            #serializer path = contract/contract_api/serializer
            serializer = InvestorRentalGalaDetailSerializer(get_contract_rental,many=True)
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
                "response": str(exception)
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)


class GetWarehouseWithUserType(APIView):
    def get(self, request,uuid,*args,**kwargs):
        try:
            get_user_type = request.query_params.get("get_user_type")
            get_company_type = request.query_params.get("company_type")
            if get_user_type == "Owner":
                get_property_qs = Property.objects.filter(
                    company__name__iexact = get_company_type,
                    get_gala__is_allotted = False,
                    get_gala__is_allotted_to_rental = False,
                    get_gala__is_allotted_to_farmer = False,
                    is_allotted_to_farmer = False).order_by("-id").values("uid","property_name").distinct()
                print(get_property_qs)
                context = {
                    "status":status.HTTP_200_OK,
                    "success":True,
                    "response":get_property_qs
                }
                return Response(
                    context,status=status.HTTP_200_OK
                )
            if get_user_type == "Investor":
                print(get_user_type)
                get_property_qs = ContractInvestor.objects.filter(
                    user__user_uid = uuid,
                    gala__warehouse__company__name = get_company_type
                ).values(
                    "gala__warehouse_id",
                    "gala__warehouse__uid",
                    "gala__warehouse__property_name"
                ).annotate(
                    uid = F("gala__warehouse__uid"),
                    property_name = F("gala__warehouse__property_name")
                    ).values("uid","property_name").order_by("-gala__warehouse_id").distinct()
                # print(get_property_qs)
                context = {
                    "status":status.HTTP_200_OK,
                    "success":True,
                    "response":get_property_qs
                }
                return Response(
                    context,status=status.HTTP_200_OK
                )
            if get_user_type == "Farmer":
                print(get_user_type)
                get_property_qs = ContractFarmer.objects.filter(
                    user__user_uid = uuid,
                    warehouse__company__name = get_company_type,
                    # warehouse__get_gala___is_allotted = False,
                    # warehouse__get_gala___is_allotted_to_rental = False,
                ).values(
                    "warehouse_id",
                    "warehouse__uid",
                    "warehouse__property_name"
                ).annotate(
                    uid = F("warehouse__uid"),
                    property_name = F("warehouse__property_name")
                    ).values("uid","property_name").order_by("-warehouse_id").distinct()
                print(get_property_qs)
                context = {
                    "status":status.HTTP_200_OK,
                    "success":True,
                    "response":get_property_qs
                }
                return Response(
                    context,status=status.HTTP_200_OK
                )
        except Exception as exception:
            context = {
                "status":status.HTTP_400_BAD_REQUEST,
                "success":False,
                "response":str(exception)
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)

class GetRemainingGalaWithUserType(APIView):
    def get(self, request, uuid, *args,**kwargs):
        try:
            get_company_type = self.request.query_params.get("company_type")
            get_user_type = self.request.query_params.get("get_user_type")
            get_warehouse_uid = self.request.query_params.get("get_warehouse_uid")
            queryset = None
            if get_user_type is not None:
                if get_user_type == "Investor":
                    queryset = ContractInvestor.objects.filter(
                        user__user_uid = uuid,
                        gala__warehouse__uid = get_warehouse_uid,
                        gala__warehouse__company__name = get_company_type,
                        gala__is_allotted = True,
                        gala__is_allotted_to_rental = False
                    ).values(
                        "gala__uid","gala__warehouse__property_name"
                    ).annotate(
                        uid = F("gala__uid"),
                         gala__uid_with_warehouse=functions.Concat(
                            F('uid'), Value(f' -- '), F('gala__warehouse__property_name'), output_field=CharField())
                    ).values("gala__uid_with_warehouse","uid")
                    context = {
                        "status":status.HTTP_200_OK,
                        "success":True,
                        "response": queryset
                    }
                    return Response(context,status=status.HTTP_200_OK)
                elif get_user_type == "Farmer":
                    queryset_list = list(ContractFarmer.objects.filter(
                        user__user_uid = uuid,
                        warehouse__uid = get_warehouse_uid,
                        warehouse__company__name = get_company_type,
                    ).values_list(
                        "warehouse",
                        flat = True
                    ))
                    queryset = Gala.objects.filter(
                        warehouse_id__in = queryset_list,

                        is_allotted_to_rental = False
                        ).values(
                            "uid","warehouse__property_name"
                        ).annotate(
                        gala__uid_with_warehouse=functions.Concat(
                            F('uid'), Value(f' -- '), F('warehouse__property_name'), output_field=CharField())
                        ).values(
                        "gala__uid_with_warehouse","uid"
                        )
                    context = {
                        "status":status.HTTP_200_OK,
                        "success":True,
                        "response": queryset
                    }
                    return Response(context,status=status.HTTP_200_OK)
                elif get_user_type == "Owner":
                    # queryset_list = list(ContractFarmer.objects.filter(
                    #     user__user_uid = uuid,
                    # ).values_list(
                    #     "warehouse",
                    #     flat = True
                    # ))
                    #need to pass company_type here when we get user type owner
                    queryset = Gala.objects.filter(
                        warehouse__uid = get_warehouse_uid,
                        warehouse__company__name = get_company_type,
                        is_allotted_to_rental = False,
                        is_allotted_to_farmer = False,
                        is_allotted = False
                        ).values(
                            "gala_number","warehouse__property_name"
                        ).annotate(
                        gala__uid_with_warehouse=functions.Concat(
                            F('gala_number'), Value(f' -- '), F('warehouse__property_name'), output_field=CharField())
                        ).values(
                        "gala__uid_with_warehouse","uid"
                        )
                    context = {
                        "status":status.HTTP_200_OK,
                        "success":True,
                        "response": queryset
                    }
                    return Response(context,status=status.HTTP_200_OK)
        except Exception as exception:
            context = {
                "status":status.HTTP_400_BAD_REQUEST,
                "success":False,
                "response":str(exception)
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)


# class GetFarmerListViewAPI(APIView):
#     def get(self,request,*args,**kwargs):
#         try:
#             get_company_type = self.request.query_params.get("company_type")
#             farmer_qs = Farmer.objects.filter(belong_to__name = get_company_type).annotate(
#                         warehouse_name = ContractFarmer.objects.filter(user__user_uid = OuterRef("user_uid")).values("warehouse__property_name"),
#                         warehouseUID = ContractFarmer.objects.filter(user__user_uid = OuterRef("user_uid")).values("warehouse__uid")
#                     ).annotate(
#                         total_gala_count = Gala.objects.filter(warehouse__uid = OuterRef("warehouseUID"),is_allotted_to_farmer=True
#                                                             ).values("warehouse__uid"
#                                                                     ).annotate(gala_count=Count("id")
#                                                                                                         ).values("gala_count"),
#                         remaining_gala_count = Gala.objects.filter(warehouse__uid=OuterRef("warehouseUID"),
#                                                                    is_allotted_to_farmer=True,
#                                                                    is_allotted=False,
#                                                                    is_allotted_to_rental=False
#                                                                     ).values("warehouse__uid"
#                                                                         ).annotate(remaining_gala_count=Count("id")
#                                                                                                         ).values("remaining_gala_count"),
#                         allotted_gala_count = Gala.objects.filter(warehouse__uid=OuterRef("warehouseUID"),
#                                                                   is_allotted_to_farmer=True,
#                                                                   is_allotted_to_rental=True,
#                                                                   is_allotted=False
#                                                                     ).values("warehouse__uid"
#                                                                         ).annotate(allotted_gala_count=Count("id")
#                                                                                                         ).values("allotted_gala_count")
#                                 )

#             serializer = TestFarmerListSerializer(farmer_qs,many=True,context = {"company_type":get_company_type})
# had to work on the below api 

class TestInvestorDetailView(APIView):
    def get(self,request,uuid,*args,**kwargs):
        try:
            get_company_type = self.request.query_params.get("company_type")

            investor_qs = AccountInvestor.objects.get(
                user_uid = "15262d8a-d00b-44b5-bbca-ca6a16633b40"
                )
            #     .investor_contract.values_list("gala_id",flat=True)
            # print(get_gala_list)
            # get_gala = Gala.objects.filter(id__in = get_gala_list).select_related(
            #     "gala_investor_contract_detail",
            #     "gala_rental_contract_detail"
            # )
            # print(get_gala)

            # print(investor_qs)
            serializer = InvestorDetailViewSerializer(investor_qs,context = {"user_uid":uuid})
            context = {
                'status':status.HTTP_200_OK,
                'success':True,
                'response':serializer.data
            }
            return Response(context,status=status.HTTP_200_OK)
        except Exception as exception:
            context = {
                'status':status.HTTP_400_BAD_REQUEST,
                'success':False,
                'response':str(exception)
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)

# import rest_framework_filters as filters

# from django_filters import rest_framework as filters

import django_filters
from django.utils.translation import gettext_lazy as _

class AccountRentalFilter(django_filters.FilterSet):
    username = django_filters.AllValuesFilter(field_name = "username",lookup_expr='iexact')
    # pubdate = django_filters.DateTimeFilter(field_name="pubdate",lookup_expr="gte")

    class Meta:
        model = AccountRental
        fields = ['username']

# class AccountRentalFilter(filters.FilterSet):
#     class Meta:
#         model = AccountRental
#         fields = {'username': ['iexact']}


class UserFilterFiltering(generics.ListAPIView):
    queryset = AccountRental.objects.all()
    serializer_class = UserRentalSerializer
    # filter_backends = (filters.DjangoFilterBackend,)
    filter_class = AccountRentalFilter




#admin dashboard view
class DashboardView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            get_company_type = self.request.query_params.get('company_type')
            get_company_instance = Company.objects.filter(
                name__iexact = get_company_type 
                ).values("uid","name").annotate(
                total_warehouse_count = Property.objects.filter(
                    company__uid = OuterRef("uid")
                    ).values("company__uid").annotate(total_warehouse_count = Count("id")).values("total_warehouse_count"),

                total_gala_count = Gala.objects.filter(warehouse__company__uid = OuterRef("uid")
                ).values("warehouse__company__uid").annotate(total_gala_count=Count("id")).values("total_gala_count"),

                total_rental_count = AccountRental.objects.filter(belong_to__uid = OuterRef("uid")
                ).values("belong_to__uid").annotate(total_rental_count=Count("id")).values("total_rental_count"),

                total_investor_count = AccountInvestor.objects.filter(belong_to__uid = OuterRef("uid")
                ).values("belong_to__uid").annotate(total_investor_count=Count("id")).values("total_investor_count"),

                total_farmer_count = Farmer.objects.filter(belong_to__uid = OuterRef("uid")
                ).values("belong_to__uid").annotate(total_farmer_count=Count("id")).values("total_farmer_count"),
                
                total_remaining_gala_count = Gala.objects.filter(warehouse__company__uid=OuterRef("uid"),
                    is_allotted_to_farmer=False,
                    is_allotted_to_rental=False,
                    is_allotted=False
                ).values("warehouse__company__uid").annotate(total_remaining_gala_count=Count("id")).values("total_remaining_gala_count"))
            serializer = DashboardViewSerializer(get_company_instance,many=True)
            context = {
                "status":status.HTTP_200_OK,
                "success":True,
                "response":serializer.data
            }
            return Response(context,status=status.HTTP_200_OK)
        except Exception as exception:
            context = {
                'status':status.HTTP_400_BAD_REQUEST,
                'success':False,
                'response':str(exception)
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST) 


class ServiceRequestUpdateView(APIView):
    def put(self, request,service_uid,*args, **kwargs):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            get_status = request.data.get('status')
            service_request_instance = ServiceRequest.objects.get(service_uid=service_uid)
            service_request_instance.status = get_status
            service_request_instance.save()
            try:
                get_registration_token = get_object_or_404(FCMDevice,user_id=service_request_instance.user.id)
                sendPush("Gala Service Request",f"Your request has been {service_request_instance.status.lower()} for service {service_request_instance} You can track status of the application by tracking id {service_request_instance.tracking_id}",[get_registration_token.registration_id])
            except Exception as exception:
                pass
            context = {
                'status':status.HTTP_200_OK,
                'success':True,
                'response':"Successfully Updated"
            }
            return Response(context, status=status.HTTP_200_OK)

        except Exception as exception:
            context = {
                'status':status.HTTP_400_BAD_REQUEST,
                'success':False,
                'response':str(exception)
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)



class ServiceRequestDetail(APIView):
    def get(self,request,service_uid=None,*args,**kwargs):
        try:
            # token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            # valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            # get_logged_in_user = valid_data['user_id']
            service_instance = ServiceRequest.objects.filter(service_uid = service_uid).select_related(
                "user","gala","service_request"
                ).prefetch_related(
                "service_request_images"
                )
            serializer = ServiceRequestSerializer(service_instance,many=True)
            context = {
                "status":status.HTTP_200_OK,
                "success":True,
                "response":serializer.data
            }
            return Response(context,status = status.HTTP_200_OK)
        except Exception as exception:
            context = {
                'status':status.HTTP_400_BAD_REQUEST,
                'success':False,
                'response':str(exception)
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST) 
        

class DashboardRentalNotificationView(APIView):
    def get(self, request,notification_uid=None,*args,**kwargs):
        try:
            if notification_uid == None:
                get_company_type = self.request.query_params.get("company_type")
                get_rental_notification = RentalNotification.objects.filter(gala__warehouse__company__name__iexact = get_company_type).select_related("rental","gala__warehouse__company")
                get_rental_notification_count  = RentalNotification.objects.filter(gala__warehouse__company__name__iexact = get_company_type,is_seen = False).count()
                serializer = DashboardRentalNotificationSerializer(get_rental_notification,many=True)
                context = {
                    "status":status.HTTP_200_OK,
                    "success":True,
                    "response":serializer.data,
                    "count":get_rental_notification_count
                }
                return Response(context,status=status.HTTP_200_OK)
            else:
                get_rental_notification = RentalNotification.objects.get(uid =notification_uid)
                get_rental_notification.is_seen = True
                get_rental_notification.save()
                context = {
                    "status":status.HTTP_200_OK,
                    "success":True,
                    "response":"Successfully Viewed!"
                }
                return Response(context,status=status.HTTP_200_OK)

       
        
        except Exception as exception:
            context = {
                'status':status.HTTP_400_BAD_REQUEST,
                'success':False,
                'response':str(exception)
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)



class LeaveRequestView(APIView):
    
    def get(self, request,leave_request_uid = None,*args,**kwargs):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            if leave_request_uid == None:
                get_company_type = self.request.query_params.get("company_type")
                get_leave_request_qs = LeaveGalaRequest.objects.filter(
                    gala__warehouse__company__name__iexact = get_company_type
                    ).select_related(
                        "user",
                        "gala__warehouse__company",
                    ).order_by("-updated_at")
                serializer = LeaveGalaRequestSerializer(get_leave_request_qs,many=True)
                get_leave_request_count = LeaveGalaRequest.objects.filter(
                    gala__warehouse__company__name__iexact = get_company_type,
                    status="Pending"
                ).count()
                context = {
                    "status":status.HTTP_200_OK,
                    "success":True,
                    "response":serializer.data,
                    "pending_leave_request_count":get_leave_request_count
                    
                }
                return Response(context,status=status.HTTP_200_OK)
            else:
                get_status = self.request.query_params.get("status")
                get_leave_request_obj = LeaveGalaRequest.objects.get(uid =leave_request_uid)
                get_leave_request_obj.status = get_status
                get_leave_request_obj.save()

                get_gala_instance = Gala.objects.get(uid = get_leave_request_obj.gala.uid)
                try:
                    get_registration_token = FCMDevice.objects.get(user_id = get_leave_request_obj.user.id)
                    sendPush(
                        "Leave Gala Request",
                        f"Your leave request for gala {get_leave_request_obj.gala.gala_number} ({get_leave_request_obj.gala.warehouse.company.name}) is {get_status.lower()}.",
                        [get_registration_token.registration_id]
                    )
                except Exception as exception:
                    pass 
                rental_notification = RentalNotification(
                    rental_id = get_logged_in_user,
                    gala = get_gala_instance,
                    status = "Leave_Gala",
                    message = f"Your leave request has been {get_status}!"
                )
                rental_notification.save()
                context = {
                    "status":status.HTTP_200_OK,
                    "success":True,
                    "response":"Successfully Updated!"
                }
                return Response(context,status=status.HTTP_200_OK)
        except Exception as exception:
            context = {
                "status":status.HTTP_400_BAD_REQUEST,
                "success":False,
                "response":str(exception)
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)
    
    def post(self,request,*args,**kwargs):
        pass


class DashboardVerticalBarChartPlot(APIView):
    def get(self,request,*args,**kwargs):
        try:
            get_company_type = self.request.query_params.get("company_type")
            get_today_date = date.today()
            get_next_year_date = get_today_date + relativedelta(years=1)
            get_contracts = ContractRental.objects.filter(
                gala__warehouse__company__name__iexact = get_company_type,
                agreement_valid_end_date__range=[get_today_date,get_next_year_date]
            ).annotate(
                month = ExtractMonth('agreement_valid_end_date'),year = ExtractYear('agreement_valid_end_date')
            ).values("month","gala__gala_area_size","gala__gala_number")
            get_contracts_df = read_frame(get_contracts)
            dates = pd.date_range(str(get_today_date),str(get_next_year_date),freq='M')
            df = pd.DataFrame()
            df['dates'] = dates
            df['month_name'] = df['dates'].dt.strftime('%b')
            df['month'] = df['dates'].dt.strftime('%m')
            df['month_year'] = df['dates'].dt.strftime('%Y')
            df['month'] = df['month'].astype(int)
            new_df = pd.merge(df, get_contracts_df, on='month',how="left")
            new_df = new_df.groupby(['month', 'month_year','month_name'], as_index=False).agg(free_gala_area_size=('gala__gala_area_size', 'sum'), gala_count=('gala__gala_number', 'count')).sort_values('month_year', ascending=True)
            new_df['month_year_name'] = new_df['month_name'] + ", " + new_df['month_year']
            new_df.fillna(0,inplace=True)
            get_month_year = new_df['month_year_name'].tolist()
            free_gala_area_size = new_df['free_gala_area_size'].tolist()
            gala_count = new_df['gala_count'].tolist()

            #  = list(map(list, zip(new_df['month_year_name'].tolist(), new_df['gala_count'].tolist())))
            pie_chart_data_points = new_df[['gala_count','month_year_name']].to_dict('index').values()
            context = {
                "status":status.HTTP_200_OK,
                "success":True,
                "response":{
                    "get_month_year":get_month_year,
                    "free_gala_area_size":free_gala_area_size,
                    "gala_count":gala_count,
                    "pie_chart_data_points":pie_chart_data_points
                }
            }
            return Response(context,status=status.HTTP_200_OK)
        except Exception as exception:
            context = {
                "status":status.HTTP_400_BAD_REQUEST,
                "success":False,
                "response":str(exception)
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)


class DashboardTotalGalaView(APIView):
    authentication_classes = []
    def get(self, request,*args, **kwargs):
        try:
            # token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            # valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            # get_logged_in_user = valid_data['user_id']
            get_company_type = self.request.query_params.get("company_type")

            get_gala_qs = Gala.objects.filter(warehouse__company__name__iexact = get_company_type).select_related(
                "warehouse","warehouse__farmer_warehouse_detail__user"
            ).prefetch_related("gala_rental_contract_detail__user","gala_rental_contract_detail__owner","gala_investor_contract_detail__user")
            
            serializer = DashboardTotalGalaSerializer(get_gala_qs,many=True) 
            context = {
                'status':status.HTTP_200_OK,
                'success':True,
                'response':serializer.data
            }
            return Response(context,status=status.HTTP_200_OK)

        except Exception as exception:
            context = {
                'status':status.HTTP_400_BAD_REQUEST,
                'success':False,
                'response':str(exception)
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)

class FreeGalaDetailViewAPI(APIView):
    authentication_classes = []
    def get(self,request,*args,**kwargs):
        try:
            get_company_type = self.request.query_params.get("company_type")
            get_month_name = self.request.query_params.get("month")
            get_year = self.request.query_params.get("year")
            get_month_number = datetime.strptime(get_month_name,"%b").month
            get_contracts_data = ContractRental.objects.filter(gala__warehouse__company__name=get_company_type,
                agreement_valid_end_date__month=get_month_number, agreement_valid_end_date__year=get_year
            )
            get_contracts = ContractRental.objects.filter(gala__warehouse__company__name=get_company_type,
                agreement_valid_end_date__month=get_month_number, agreement_valid_end_date__year=get_year
            ).aggregate(free_gala_area_size = Sum('gala__gala_area_size'))
            serializer = InvestorRentalGalaDetailSerializer(get_contracts_data,many=True)
            context = {
                    'status':status.HTTP_200_OK,
                    'success':True,
                    'response':serializer.data,
                    'gala_free_area_size':get_contracts['free_gala_area_size']
                }
            return Response(context,status=status.HTTP_200_OK)
        except Exception as exception:
            context = {
                'status':status.HTTP_400_BAD_REQUEST,
                'success':False,
                'response':str(exception)
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)



class FarmerUpdateView(APIView):
    def put(self, request,farmer_uuid,*args, **kwargs):
        try:
            # token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            # valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            # get_logged_in_user = valid_data['user_id']
            get_farmer_instance = AccountFarmer.objects.get(user_uid = farmer_uuid)

            serializer = FarmerUpdateSerializer(get_farmer_instance,data=request.data,partial=True)
            if serializer.is_valid():
                serializer.save()
                context = {
                    'status': status.HTTP_200_OK,
                    'success':True,
                    'response':serializer.data
                }
                return Response(context,status=status.HTTP_200_OK)

            else:
                serializer_errors = {key: value[0] for key, value in serializer.errors.items()}
                context = {
                    'status':status.HTTP_400_BAD_REQUEST,
                    'success':False,
                    'response':serializer_errors
                }
                return Response(context,status=status.HTTP_400_BAD_REQUEST)

        except Exception as exception:
            context = {
                'status':status.HTTP_400_BAD_REQUEST,
                'success':False,
                'response':str(exception)
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)



class InvestorUpdateView(APIView):

    def put(self, request,investor_uuid,*args, **kwargs):
        try:
            # token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            # valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            # get_logged_in_user = valid_data['user_id']
            get_investor_instance = AccountInvestor.objects.get(user_uid=investor_uuid)

            serializer = InvestorUpdateSerializer(get_investor_instance,data=request.data,partial=True)
            if serializer.is_valid():
                serializer.save()
                context = {
                    'status':status.HTTP_200_OK,
                    'success':True,
                    'response':serializer.data
                }
                return Response(context,status=status.HTTP_200_OK)

            else:
                serializer_errors = {key: value[0] for key, value in serializer.errors.items()}
                context = {
                    'status':status.HTTP_400_BAD_REQUEST,
                    'success':False,
                    'response':serializer_errors
                }
                return Response(context,status=status.HTTP_400_BAD_REQUEST)

        except Exception as exception:
            context = {
                'status':status.HTTP_400_BAD_REQUEST,
                'success':False,
                'response':str(exception)
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)


class DashboardTotalRemainingGala(APIView):
    # authentication_classes = []
    def get(self, request,*args, **kwargs):
        try:
            # token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            # valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            # get_logged_in_user = valid_data['user_id']
            get_company_type = self.request.query_params.get("company_type")

            get_remaining_galas = Gala.objects.filter(
                                            Q(is_allotted_to_farmer=False) | Q(is_allotted_to_farmer=True),
                                            warehouse__company__name=get_company_type,
                                            is_allotted=False,
                                            is_allotted_to_rental=False).select_related('warehouse','warehouse__farmer_warehouse_detail','warehouse__farmer_warehouse_detail__user')
            serializer = DashboardTotalRemainingGalaSerializer(get_remaining_galas,many=True)
            context = {
                'status':status.HTTP_200_OK,
                'success':True,
                'response':serializer.data
            }
            return Response(context, status=status.HTTP_200_OK)

        except Exception as exception:
            context = {
                'status':status.HTTP_400_BAD_REQUEST,
                'success':False,
                'response':str(exception)
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)


# 08/02/2023
class PropertyUpdateView(APIView):
    def put(self,request,uuid,*args,**kwargs):
        try:
            get_property_instance = Property.objects.get(uid = uuid)
            # print(get_property_instance,17)
            serializer = UpdatePropertySerializer(get_property_instance,data=request.data,partial=True)
            # print(serializer.initial_data)
            if serializer.is_valid():
                serializer.save()
                context = {
                    'status':status.HTTP_200_OK,
                    'success':True,
                    'response':serializer.data
                }
                return Response(context,status=status.HTTP_200_OK)

            else:
                serializer_errors = serializer.errors
                serializer_errors = {key: value[0] for key, value in serializer_errors.items()}
                context = {
                    'status':status.HTTP_400_BAD_REQUEST,
                    'success':False,
                    'response':serializer_errors
                }
                return Response(context,status=status.HTTP_400_BAD_REQUEST)
        except Exception as exception:
            context = {
                'status':status.HTTP_400_BAD_REQUEST,
                'success':False,
                'response':str(exception)
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)

class ServiceListAPIForAdmin(viewsets.ViewSet):
    # authentication_classes = []
   
    def list(self, request):
        try:
            # token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            # valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            # get_logged_in_user = valid_data['user_id']
            queryset = get_list_or_404(Service)
            serializer = ServiceSerializer(queryset,many=True)
            context ={
                'status':status.HTTP_200_OK,
                'success':True,
                'response':serializer.data
            }
            return Response(context,status=status.HTTP_200_OK)
        except Exception as exception:
            context = {
                'status':status.HTTP_400_BAD_REQUEST,
                'success':False,
                'response':str(exception)
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)

class ServiceRequestUpdateView(APIView):
    def put(self, request,service_uid,*args, **kwargs):
        try:

            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            print(service_uid,get_logged_in_user)
            get_status = request.data.get('status')
            service_request_instance = ServiceRequest.objects.get(service_uid=service_uid)
            service_request_instance.status = get_status
            service_request_instance.save()
            try:
                get_registration_token = get_object_or_404(FCMDevice,user_id=service_request_instance.user.id)
                sendPush("Gala Service Request",f"Your request has been {service_request_instance.status.lower()} for service {service_request_instance} You can track status of the application by tracking id {service_request_instance.tracking_id}",[get_registration_token.registration_id])
            except Exception as exception:
                pass
            context = {
                'status':status.HTTP_200_OK,
                'success':True,
                'response':"Successfully Updated"
            }
            return Response(context, status=status.HTTP_200_OK)

        except Exception as exception:
            context = {
                'status':status.HTTP_400_BAD_REQUEST,
                'success':False,
                'response':str(exception)
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)

class AdminProfileView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            get_admin_obj = Owner.objects.get(is_superuser=True)
            serializer = AdminProfileSerializer(get_admin_obj)
            context = {
                'status':status.HTTP_200_OK,
                'success':True,
                'response':serializer.data
            }
            return Response(context, status=status.HTTP_200_OK)

        except Exception as exception:
            context = {
                'status':status.HTTP_400_BAD_REQUEST,
                'success':False,
                'response':str(exception)
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)

class AdminProfileUpdateView(APIView):
    authentication_classes = []
    def put(self, request,*args, **kwargs):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']

            get_admin_obj = Owner.objects.get(id = get_logged_in_user)
            print(get_admin_obj,17)

            get_profile_image = request.FILES.get('profile_image')

            serializer = AdminProfileUpdateSerializer(get_admin_obj,data=request.data,partial=True,context= {"profile_image":get_profile_image})
            if serializer.is_valid():
                serializer.save()
                context = {
                    'status':status.HTTP_200_OK,
                    'success':True,
                    'response':"Successfully Updated"
                }
                return Response(context, status=status.HTTP_200_OK)

            else:
                serializer_errors = {key: value[0] for key, value in serializer.errors.items()}
                context = {
                    "status":status.HTTP_400_BAD_REQUEST,
                    "success":False,
                    "response":serializer_errors
                }
                return Response(context,status=status.HTTP_400_BAD_REQUEST)

        except Exception as exception:
            context = {
                'status':status.HTTP_400_BAD_REQUEST,
                'success':False,
                'response':str(exception)
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        
class GetRenewGalaRequestView(APIView):
    authentication_classes = []
    def get(self, request, *args, **kwargs):
        try:
            # token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            # valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            # get_logged_in_user = valid_data['user_id']
            
            get_company_type = self.request.query_params.get('company_type')

            get_renew_request_qs = RenewGalaRequest.objects.filter(
                    renew_gala__warehouse__company__name__iexact=get_company_type
                    ).select_related(
                        "renew_user",
                        "renew_gala__warehouse__company",
                    
            ).annotate(
                uid = ContractRental.objects.filter(gala__uid=OuterRef("renew_gala__uid")).values("uid"),
                agreement_valid_doc = ContractRental.objects.filter(gala__uid=OuterRef("renew_gala__uid")).values("agreement_valid_doc"),
                agreement_valid_start_date = ContractRental.objects.filter(gala__uid=OuterRef("renew_gala__uid")).values("agreement_valid_start_date"),
                agreement_valid_end_date = ContractRental.objects.filter(gala__uid=OuterRef("renew_gala__uid")).values("agreement_valid_end_date"),
                ghar_patti_doc = ContractRental.objects.filter(gala__uid=OuterRef("renew_gala__uid")).values("ghar_patti_doc"),
                ghar_patti_start_date = ContractRental.objects.filter(gala__uid=OuterRef("renew_gala__uid")).values("ghar_patti_start_date"),
                ghar_patti_end_date = ContractRental.objects.filter(gala__uid=OuterRef("renew_gala__uid")).values("ghar_patti_end_date"),
                gala = ContractRental.objects.filter(gala__uid=OuterRef("renew_gala__uid")).values("gala__gala_number"),
                owner = ContractRental.objects.filter(gala__uid=OuterRef("renew_gala__uid")).values("owner__username"),
                warehouse = ContractRental.objects.filter(gala__uid=OuterRef("renew_gala__uid")).values("gala__warehouse__property_name"),
                rental = ContractRental.objects.filter(gala__uid=OuterRef("renew_gala__uid")).values("user__username")
            )

            serializer = RenewGalaRequestSerializer(get_renew_request_qs,many=True)
            context = {
                'status':status.HTTP_200_OK,
                'success':True,
                'response':serializer.data
            }
            return Response(context,status=status.HTTP_200_OK)

        except Exception as exception: 
            context = {
                'status': status.HTTP_400_BAD_REQUEST,
                'success':False,
                'response': str(exception)
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)