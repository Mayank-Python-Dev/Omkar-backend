from django.urls import path
from rest_framework_simplejwt import views as jwt_views
# from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    MyObtainTokenPairView
)
from superadmin.superadmin_api.views import (
    InvestorDetailView,
    FarmerDetailView,
    RentalDetailView,
    RemainingPropertyView,
    EmployeeDetailView,
    CompanyAPI,
    ContractInvestorDetailView,
    ContractRentalDetailView,
    PropertyDetailView,
    LeaveAndLicenseDetailView,
    InvestorWarehousesView,
    FarmerWarehousesView,
    FarmerRemainingGalaDetailView,
    RentalWarehousesView,
    InvestorsGalaDetailView,
    OwnerWarehouseView,
    
    InvestorsGalaDetailView,
    FarmersGalaDetailViewAPI,
    RentalsServiceRequestDetailView,

    #Owners__Developer_tab_url
    OwnerInvestorContractDetailView,
    OwnerRentalContractDetailView,
    OwnerRemainingGalaDetail,
    # OwnerTotalRemainingGalaCount,
    
    #Live_and_License_tab_uls
    RentalGalaDetail,

    LiveAndLicenseWarehouseView,
    LiveAndLicenseDetailView,

    RentalWarehouseAndGalaView,
    RentalWarehouseAndGalaDetailView,

    InvestorRegistration,

    AddPropertyView,
    PropertyListView,
    
    AddGalaView,
    FarmerListView,
    
    AddContractWithFarmerView,
    GetUsersWithUserType,

    GetGalaWithUserUUID,
    #list api's
    InvestorListAPIView,
    RentalListAPI,
    OwnerPropertyListAPI,
    OwnerPropertyGalaListAPI,
    GetFarmerListViewAPI,

    # ContractInvestorPostAPI
    ContractInvestorPostAPI,
    GetPropertyTypeView,
    GetGalaWithPropertyUID,

    ContractWithRental,

    #update api's
    GalaUpdateView,

    # TestAPI
    GetRentalWithCompanyTypeAPI,
    FarmerGalaDetailView,

    InvestorListView,
    InvestorGalaDetailView,
    GetWarehouseWithUserType,
    GetRemainingGalaWithUserType,


    GetFarmerListViewAPI,

    UserFilterFiltering,
    DashboardView,
    ServiceRequestDetail,
    ServiceRequestUpdateView,
    OwnerPropertyListForFarmerAPI,

    DashboardRentalNotificationView,
    LeaveRequestView,
    TestInvestorDetailView,
    InvestorRemainingGalaView,
    InvestorRentalDetailView,
    TokenRefreshView,
    DashboardVerticalBarChartPlot,
    DashboardTotalGalaView,
    FreeGalaDetailViewAPI,
    FarmerUpdateView,
    InvestorUpdateView,
    DashboardTotalRemainingGala,
    PropertyUpdateView,
    ServiceListAPIForAdmin,
    AdminProfileView,
    AdminProfileUpdateView,
    GetRenewGalaRequestView,
    ContractRentalUpdateView

)
urlpatterns = [
    path('login/', MyObtainTokenPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("get-companies/",CompanyAPI.as_view({"get":"list"}),name="get-company"),
    path("get-investor-users/",InvestorDetailView.as_view(),name="get-investor-users"),
    path("get-rental-users/",RentalDetailView.as_view(),name="get-rentals-user"),
    path("get-employees/",EmployeeDetailView.as_view(),name="get-employees"),
    path("get-contract-investor-detail/<str:uuid>/",ContractInvestorDetailView.as_view(),name="get-contract-investor-detail"),
    path("get-contract-rental-detail/<str:uuid>/",ContractRentalDetailView.as_view(),name="get-contract-rental-detail"),
    path("get-property-detail/",PropertyDetailView.as_view(),name="get-property-detail"),
    
    path("get-leave-and_license-detail/<str:uuid>/",LeaveAndLicenseDetailView.as_view(),name="get-leave-and_license-detail"),
    #19 Dec 2022
    path("get-investors-warehouses/",InvestorWarehousesView.as_view(),name="get-investors-warehouses"),
    
    path("get-rentals-warehouses/",RentalWarehousesView.as_view(),name="get-rental-warehouses"),
    path("get-investors-gala-detail/<str:uuid>/",InvestorsGalaDetailView.as_view(),name="get-investors-gala-detail"),
    # path("get-owner-gala-detail/<str:uuid>/",OwnerGalaDetailView.as_view(),name = "get-owner-gala-detail"),
    path("get-remaining-property/",RemainingPropertyView.as_view(),name="get-remaining-property"),
    # path("get-contract-detail/",)
    # path("get-investors-gala-detail/<str:uuid>/",InvestorsGalaDetailView.as_view(),name="get-investors-gala-detail"),
    path("get-farmers-gala-detail/<str:uuid>/<str:warehouse_uid>/",FarmersGalaDetailViewAPI.as_view(),name="get-farmers-gala-detail"),
    path('get-allrentals-service-request/',RentalsServiceRequestDetailView.as_view(),name="get-alluser-service-request"),
    
    # path('get-allrentals-service-request/',RentalsServiceRequestDetailView.as_view(),name="get-allrentals-service-request"),

    #Owners__Developer_tab_url
    path("get-owner-warehouses/",OwnerWarehouseView.as_view(),name = "get-owner-warehouses"),
    path("get-owner-investor-contract-detail/<str:uuid>/",OwnerInvestorContractDetailView.as_view(),name="get-owner-investor-contract-detail"),
    path("get-owner-rental-contract-detail/<str:uuid>/",OwnerRentalContractDetailView.as_view(),name="get-owner-rental-contract-detail"),
    path("get-owner-remaining-gala-detail/<str:uuid>/",OwnerRemainingGalaDetail.as_view(),name="get-owner-remaining-gala-detail"),
    # path("get-owner-total-remaining-gala-count/",OwnerTotalRemainingGalaCount.as_view(),name="get-owner-total-remaining-gala-count"),
    #Live_and_License_tab_urls
    path("get-live-and-license-warehouses/",LiveAndLicenseWarehouseView.as_view(),name="get-live-and-license-warehouses"),
    path("get-live-and-license-detail-api/<str:uuid>/",LiveAndLicenseDetailView.as_view(),name="get-live-and-license-detail-api"),
    path("test",RentalGalaDetail.as_view(),name="test"),
    path("get-rental-users-warehouse/",RentalWarehouseAndGalaView.as_view(),name="get-rental-users-warehouse"),
    path("get-rental-warehouse-detail/<str:uuid>/",RentalWarehouseAndGalaDetailView.as_view(),name="get-rental-warehouse-detail"),

    path("investor-register/",InvestorRegistration.as_view(),name="investor-register"),

    #add property api 
    path("add-property-api/",AddPropertyView.as_view(),name="add-property-api"),
    path("get-property-list/",PropertyListView.as_view(),name="get-property-list"),
    path("get-gala-with-property-uid/<slug:property_uid>/",GetGalaWithPropertyUID.as_view(),name="get-gala-with-property-uid"),
    path("add-gala-api/",AddGalaView.as_view(),name="add-gala-api"),
    
    path("create-contract-with-farmer/",AddContractWithFarmerView.as_view(),name="create-contract-with-farmer"),
    #for contract with rental
    path("get-users-with-usertype/",GetUsersWithUserType.as_view(),name="get-users-with-usertype"),
    path("get-gala-with-usertype/<str:uuid>/",GetGalaWithUserUUID.as_view(),name='get-gala-with-userype'),

    # path("create-contract-with-farmer/")
    # path()
    path("get-property-type/",GetPropertyTypeView.as_view(),name="get-property-type"),
    #ContractInvestor list api's 
    path("get-investor-list/",InvestorListAPIView.as_view(),name = "get-investor-list"),
    path("get-rental-list/",RentalListAPI.as_view(),name = "get-rental-list"),
    path("get-owner-warehouse-list/",OwnerPropertyListAPI.as_view({'get':'list'}),name = "get-owner-warehouse-list"),
    path("get-owner-warehouse-list-for-farmer/",OwnerPropertyListForFarmerAPI.as_view({'get':'list'}),name = "get-owner-warehouse-list-for-farmer"),
    
    path("get-owner-warehouse-galas/<str:uuid>/",OwnerPropertyGalaListAPI.as_view(),name ="get-owner-warehouse-galas"),
    
    #ContractInvestor post api
    path("investor-contract-post-api/",ContractInvestorPostAPI.as_view(),name = "investor-contract-post-api"),
    path("contract-with-rental/",ContractWithRental.as_view(),name = "contract-with-rental"),
    path("gala-update-api/<str:uuid>/",GalaUpdateView.as_view(),name="gala-update-api"),
    path("get-rental-list-with-company_type/",GetRentalWithCompanyTypeAPI.as_view(),name = "get-rental-list-with-company"),
    # path("test-api/",TestAPI.as_view(),name = "test-api"),

    # farmer api's
    path("get-farmer-user/",FarmerDetailView.as_view(),name="get-farmer-user"),
    path("get-farmer-list/",FarmerListView.as_view(),name="get-farmer-list"),
    path("get-farmers-warehouses/",FarmerWarehousesView.as_view(),name="get-farmers-warehouses"),
    path("get-farmers-list-api/", GetFarmerListViewAPI.as_view(),name="get-farmers-list-api"),
    path("get-farmer-remaining-galas-detail/<str:uuid>/",FarmerRemainingGalaDetailView.as_view(),name='get-farmer-remaining-galas-detail'),
    # path("get-farmer-allotted-gala/<str:uuid>/",),
    path("get-farmers-gala-detail/<str:uuid>/",FarmersGalaDetailViewAPI.as_view(),name="get-farmers-gala-detail"),
    # path("get-farmer-gala-detail/<str:uuid>/",FarmerGalaDetailView.as_view(),name="get-farmer-gala-detail"),
    # path("test-api/",TestAPI.as_view(),name = "test-api"),

    #investor list and property
    path("get-investor-list-with-company/",InvestorListView.as_view(),name="get-investor-list-with-company"),
    path("get-investor-rental-gala-detail-view/<str:uuid>/",InvestorGalaDetailView.as_view(),name="get-investor-rental-gala-detail-view"),
    path("get-warehouse-with-usertype/<str:uuid>/",GetWarehouseWithUserType.as_view(),name="get-warehouse-with-usertype"),
    path("get-remaining-gala-with-usertype/<str:uuid>/",GetRemainingGalaWithUserType.as_view(),name="get-remaining-gala-with-usertype"),

    path("get-farmers-list-api/", GetFarmerListViewAPI.as_view(),name="get-farmers-list-api"),

    path("filtering-rental/",UserFilterFiltering.as_view(),name="filtering-rental"),

    path("dashboard-view/",DashboardView.as_view(),name="dashboard-view"),
    path("service-detail-view/<str:service_uid>/",ServiceRequestDetail.as_view(),name="service-detail-view"),
    path("service-update-view/<str:service_uid>/",ServiceRequestUpdateView.as_view(),name="service-detail-view"),

    path("get-rental-notifications/",DashboardRentalNotificationView.as_view(),name="get-rental-dashboard-notifications"),
    path("get-rental-notifications/<str:notification_uid>/",DashboardRentalNotificationView.as_view(),name="get-rental-dashboard-notifications"),
    path("get-leave-request/",LeaveRequestView.as_view(),name="get-leave-request"),
    path("get-leave-request/<str:leave_request_uid>/",LeaveRequestView.as_view(),name="get-leave-request"),

    # path("update-service-request-api/",)
    path("get-investor-remaining-gala-detail/<str:uuid>/",InvestorRemainingGalaView.as_view(),name="get-investor-remaining-gala-detail"),
    path("get-investor-rental-detail/<str:uuid>/",InvestorRentalDetailView.as_view(),name="get-investor-rental-detail"),

    path("get-investor-rental-gala-detail-view/<str:uuid>/",InvestorGalaDetailView.as_view(),name="get-investor-rental-gala-detail-view"),
    path('update-investor-profile/<str:investor_uuid>/',InvestorUpdateView.as_view(),name="update-investor-profile"),#13/03/2023
    path('update-farmer-profile/<str:farmer_uuid>/',FarmerUpdateView.as_view(),name="update-farmer-profile"),



    path("property-update-api/<str:uuid>/",PropertyUpdateView.as_view(),name="property-update-api"),
    path("get-investor-gala-detail-api/<str:uuid>/",TestInvestorDetailView.as_view(),name="get-investor-gala-detail-api"),
    path("get-vertical-bat-plot-datapoints/",DashboardVerticalBarChartPlot.as_view(),name="get-vertical-bat-plot-datapoints"),

    path("get-service-list-for-admin/",ServiceListAPIForAdmin.as_view({"get":"list"}),name="get-service-list-for-admin"),

    path("update-service-request/<str:request_uuid>/",ServiceRequestUpdateView.as_view(),name="update-service-request"),
    path("get-admin-profile/",AdminProfileView.as_view(),name="get-admin-profile"),
    path("update-admin-profile/",AdminProfileUpdateView.as_view(),name="update-admin-profile"),

    path('get-renew-request/',GetRenewGalaRequestView.as_view(),name="get-renew-request"), #01/03/2023
    path('update-rental-contract/<str:contract_uuid>/<str:renew_uuid>/',ContractRentalUpdateView.as_view(),name="update-rental-contract"),


    path("get-total-galas/",DashboardTotalGalaView.as_view(),name="get-total-galas"),
    path("get-total-remaining-galas/",DashboardTotalRemainingGala.as_view(),name="get-total-remaining-galas"),#14/03/2023

    path("get-free-gala-detail-view/",FreeGalaDetailViewAPI.as_view(),name="get-free-gala-detail-view")
    
    
]

# print(len(urlpatterns))