from rest_framework.views import APIView
from notification.models import (
    RentalNotification
)
from .serializers import (
    RentalNotificationSerializer
)
from rest_framework_simplejwt.backends import TokenBackend
from rest_framework.response import Response
from rest_framework import (
    status
)


class RentalNotificationView(APIView):
    def get(self, request, user_uid, *args, **kwargs):
        try:
            # token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            # valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            # get_logged_in_user = valid_data['user_id']
            get_rental_notification_instance = RentalNotification.objects.filter(rental__user_uid = user_uid).order_by("-id")
            serializer = RentalNotificationSerializer(get_rental_notification_instance,many=True)
            context = {
                "status":status.HTTP_200_OK,
                "success":True,
                "response":serializer.data
            }
            return Response(context,status=status.HTTP_200_OK)
        except Exception as exception:
            context = {
                'status': status.HTTP_400_BAD_REQUEST,
                'success': False,
                'response': str(exception)
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)

        