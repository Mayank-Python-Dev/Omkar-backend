import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from notification.models import (
    RentalNotification
)
# from notification.notification_api.serializers import (
#     RentalNotificationSerializer
# )

from notification.notification_api.serializers import (
    DashboardRentalNotificationSerializer
)


class DashboardConsumer(WebsocketConsumer):

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_code']
        self.group_name = 'room_%s' % self.room_name
        # print(self.group_name)

        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )
        self.accept()
        get_rental_notification = RentalNotification.objects.filter(gala__warehouse__company__name__iexact = self.room_name).select_related("rental","gala__warehouse__company")
        serializer = DashboardRentalNotificationSerializer(get_rental_notification,many=True)
        get_rental_notification_seen_count = RentalNotification.objects.filter(gala__warehouse__company__name__iexact = self.room_name,is_seen=False).count()
        self.send(text_data=json.dumps( 
                {
                    "type":"connection_established",
                    "message":"you are connected now!",
                    "payload":{
                        "data":serializer.data,
                        "is_seen_count":get_rental_notification_seen_count
                    }
                }
            ))
        

    def receive(self,text_data):
        load_text_data = json.loads(text_data)
        get_rental_notification = RentalNotification.objects.get(uid = load_text_data['uid'])
        get_rental_notification.is_seen = True
        get_rental_notification.save()
        get_rental_notification = RentalNotification.objects.filter(gala__warehouse__company__name__iexact = load_text_data['company_name']).select_related("rental","gala__warehouse__company")
        serializer = DashboardRentalNotificationSerializer(get_rental_notification,many=True)
        get_rental_notification_seen_count = RentalNotification.objects.filter(gala__warehouse__company__name__iexact = self.room_name,is_seen=False).count()
        if serializer:
            self.send(text_data=json.dumps( 
                {
                    "type":"connection_established",
                    "message":"you are connected now!",
                    "payload":{
                        "data":serializer.data,
                        "is_seen_count":get_rental_notification_seen_count
                    }
                }
            ))
        else:
            self.send(text_data=json.dumps( 
                {
                    "type":"connection_established",
                    "message":"you are connected now!",
                    "payload":{
                        "data":[],
                        "is_seen_count":None
                    }
                }
            ))

    #     get_profile_instance = get_object_or_404(Profile,user_uid=self.room_name)
    #     get_alert_instance_qs = Alert.objects.filter(user_id=get_profile_instance.user.id,is_matched=False).order_by("-id")
    #     serializer = AlertSerializer(get_alert_instance_qs,many=True)
    #     if serializer:
    #         self.send(text_data=json.dumps( 
    #             {
    #                 "type":"connection_established",
    #                 "message":"you are connected now!",
    #                 "payload":serializer.data
    #             }
    #         ))
    #     else:
    #         self.send(text_data=json.dumps( 
    #             {
    #                 "type":"connection_established",
    #                 "message":"you are connected now!",
    #                 "payload":[]
    #             }
    #         ))


    def update_notification_instance(self,text_data):
        # load_text_data = json.loads(text_data)
        # print(load_text_data,113)
        # get_profile_instance = get_object_or_404(Profile,user_uid=text_data['text'])
        # get_alert_instance_qs = Alert.objects.filter(user_id=get_profile_instance.user.id,is_matched=False).order_by("-id")
        # serializer = AlertSerializer(get_alert_instance_qs,many=True)
        get_rental_notification = RentalNotification.objects.filter(gala__warehouse__company__name__iexact = self.room_name).select_related("rental","gala__warehouse__company")
        serializer = DashboardRentalNotificationSerializer(get_rental_notification,many=True)
        get_rental_notification_seen_count = RentalNotification.objects.filter(gala__warehouse__company__name__iexact = self.room_name,is_seen=False).count()
        if serializer:
            self.send(text_data=json.dumps( 
                {
                    "type":"connection_established",
                    "message":"you are connected now!",
                    "come_from_celery":True,
                    "payload":{
                        "data":serializer.data,
                        "is_seen_count":get_rental_notification_seen_count
                    }
                }
            ))
        else:
            self.send(text_data=json.dumps( 
                {
                    "type":"connection_established",
                    "message":"you are connected now!",
                    "come_from_celery":True,
                    "payload":{
                        "data":[],
                        "is_seen_count":None
                    },
                    
                }
            ))

    def disconnect(self,close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )