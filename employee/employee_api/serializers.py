from rest_framework import serializers
from employee.models import (
    Employee
)

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['uid','name','contact_no','address','city','zipcode']