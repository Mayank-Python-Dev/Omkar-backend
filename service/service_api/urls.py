from django.urls import path
from service.service_api.views import (
   ServiceListAPI,
   SubServiceListAPI,
   ServiceRequestView,
 
   RentalServiceRequestStatus,
   RentalProperties,
   RentalNotificationView,
   RentalAllServiceRequest,
   RentalGetServiceRequest,
   LeaveGalaRequestAPI,
   RentalGetGalaAPI,
   ViewContract,
   ViewContractDetail,
   GetGalaForLeaveRequest,
   RenewRequestView,
  
)

urlpatterns = [

    path('get-service-list/', ServiceListAPI.as_view({"get":"list","post":"create"}), name='get-service-list'),
    path('get-subservice-list/', SubServiceListAPI.as_view({"get":"list","post":"create"}), name='get-subservice-list'),
    path('get-service-request/',ServiceRequestView.as_view(),name="get-service-request"),
   
    path('post-service-request/',ServiceRequestView.as_view(),name="post-service-request"),
    path('leave-service-request/',RentalServiceRequestStatus.as_view(),name="leave-service-request"),
    path('track-status/',RentalServiceRequestStatus.as_view(),name="track-status"),
    
    path('leave-gala-request/',LeaveGalaRequestAPI.as_view() ,name="leave-gala-request"),
    path('rental-get-gala/',RentalGetGalaAPI.as_view() ,name="rental-get-gala"),
    
    path('get-leave-gala-request/',LeaveGalaRequestAPI.as_view(),name="get-leave-gala-request"),
    
    path('get-rental-properties/',RentalProperties.as_view(),name="get-rental-properties"),
    path('get-rental-notification/',RentalNotificationView.as_view(),name="get-rental-properties"),
    path('get-rental-all-request/', RentalAllServiceRequest.as_view(),name="get-rental-all-request"),
    path('get-rental-request-detail/<str:user_uid>/<str:tracking_id>/',RentalGetServiceRequest.as_view(),name="get-rental-request-details"),
    path("view-contract/<str:uuid>/",ViewContract.as_view(),name="view-contract"),
    path("view-contract-detail/<str:uuid>/",ViewContractDetail.as_view(),name="view-contract-detail"),

    path("get-gala-for-leave-request/",GetGalaForLeaveRequest.as_view(),name="get-gala-for-leave-request"),

    path('post-renew-request/',RenewRequestView.as_view(),name="post-renew-request"), #01/03/2023

]
