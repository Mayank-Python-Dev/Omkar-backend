from notification.models import (
    RentalNotification
)

from rest_framework import serializers
from account.account_api.serializers import (
    DashboardAccountRentalListSerializer
)
from warehouse.warehouse_api.serializers import (
    InvestorPropertyGalaSerializer
)

class RentalNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model  = RentalNotification
        fields = ['message','get_date_time']


class DashboardRentalNotificationSerializer(serializers.ModelSerializer):
    rental = DashboardAccountRentalListSerializer()
    gala = InvestorPropertyGalaSerializer()
    
    class Meta:
        model = RentalNotification
        fields = ['uid','rental','gala','status','is_seen','sub_service_name','get_date_time']
    
    def to_representation(self,instance):
        response = super(DashboardRentalNotificationSerializer,self).to_representation(instance)
        if response['sub_service_name'] == None:
            response['sub_service_name'] = ""
        if response['status'] == "Service_Gala":
            response['message'] = f"{response['rental']['first_name']} {response['rental']['last_name']} has requested for {response['sub_service_name']} on {response['gala']['gala_number']} ({response['gala']['warehouse']['property_name']})"
        if response['status'] == "Leave_Gala":
            response['message'] = f"{response['rental']['first_name']} {response['rental']['last_name']} wants to leave gala {response['gala']['gala_number']} ({response['gala']['warehouse']['property_name']})"
        if response['status'] == "Renew_Gala":
            response['message'] = f"{response['rental']['first_name']} {response['rental']['last_name']} wants to renew contract for gala number {response['gala']['gala_number']} of {response['gala']['warehouse']['property_name']}"
        return response