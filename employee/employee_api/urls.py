from django.urls import path
from employee.employee_api.views import (
    EmployeeRegisterAPI
)

urlpatterns = [
    path("employee-register/",EmployeeRegisterAPI.as_view(),name="employee-register"),
]