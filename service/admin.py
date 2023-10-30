from django.contrib import admin
from service.models import (
    Service,
    SubService,
    ServiceRequest,
    Image,
    LeaveGalaRequest,
    RenewGalaRequest,
   
)


class ServiceAdmin(admin.ModelAdmin):
    list_display = ('service_uid','service_name')


class SubServiceAdmin(admin.ModelAdmin):
    list_display = ('service_uid','service','sub_service_name')
    # search_fields = ('sub_service_uid','sub_service_name')
    # list_filter = ('sub_service_uid','sub_service_name')
    ordering = ('service_uid',)


class ServiceRequestAdmin(admin.ModelAdmin):
     model=ServiceRequest
     list_display = ('tracking_id','user','request_sub_service','gala','service_request_date','get_date_time','get_status','description','status')


class LeaveGalaRequestAdmin(admin.ModelAdmin):
    model=LeaveGalaRequest
    list_display = ('user','gala','reason_for_leaving','status','created_at','updated_at')
admin.site.register(LeaveGalaRequest,LeaveGalaRequestAdmin)

class ImageAdmin(admin.ModelAdmin):
     model=Image
     list_display = ('service_request','image')


class RenewGalaRequestAdmin(admin.ModelAdmin):
    list_display = ['renew_uid','renew_user','renew_gala','renew_status']



admin.site.register(Image, ImageAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(SubService, SubServiceAdmin)
admin.site.register(ServiceRequest, ServiceRequestAdmin)
admin.site.register(RenewGalaRequest,RenewGalaRequestAdmin)