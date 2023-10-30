from rest_framework.views import APIView

from employee.employee_api.serializers import (
    EmployeeSerializer
)

class EmployeeRegisterAPI(APIView):
    authentication_classes = []
    def post(self, request,*args, **kwargs):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            valid_data = TokenBackend(algorithm='HS256').decode(token,verify=False)
            get_logged_in_user = valid_data['user_id']
            get_employee_data = request.data
            serializer = EmployeeSerializer(data = get_employee_data)
            if serializer.is_valid():
                serializer.save()
                context = {
                    'status':status.HTTP_200_OK,
                    'success':True,
                    'response':'hello world!'
                }
                return Response(context,status=status.HTTP_200_OK)

        except Exception as exception:
            context = {
                'status':status.HTTP_400_BAD_REQUEST,
                'success':False,
                'response':str(exception)
            }
            return Response(context,status=status.HTTP_400_BAD_REQUEST)

