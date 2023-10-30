"""OmkarProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import (
    path,
    include,
    re_path
)
from .views import (
    home,
    # dashboard
)
from django.views.generic import TemplateView
from superadmin.views import (
    get_bar_chart
)

# react_views_regex = r'\/|\b'.join([

#     # List all your react routes here
#     'tenants/',
#     'dashboard/',
#     'leaveAndLicense/',
#     'leaveAndLicense/<str:uuid>/',

# ]) + r'\/'

# print(react_views_regex)

# re_path(react_views_regex, TemplateView.as_view(template_name="out/index.html")),

from django.conf import settings
# from superadmin.helpers import check_contract_rental

# react_routes = getattr(settings, 'REACT_ROUTES', [])


urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html")),
    # path("check",check_contract_rental),
    # re_path(r"^$", home),
    
    # path("",TemplateView.as_view(template_name="index.html")),
    # path("companyCategory",TemplateView.as_view(template_name="companyCategory/index.html")),

    # path("companyCategory",TemplateView.as_view(template_name="companyCategory/index.html")),
    # path("dashboard",dashboard,name="dashboard"),
    
    # re_path("(!_next).*/", include("superadmin.superadmin_api.urls")),
    # re_path(r'^/((?!_next).*)/(.+?)(?:/)?$', home),
    path("admin/", admin.site.urls),
    path('__debug__/', include('debug_toolbar.urls')),
    path("admin-api/",include("superadmin.superadmin_api.urls")),
    path("user/",include("account.account_api.urls")),
    path("employee-api/",include("employee.employee_api.urls")),
    path("service-api/",include("service.service_api.urls")),
    path("get-bar-chart/",get_bar_chart,name="get_bar_chart"),
    # re_path(r"^$", TemplateView.as_view(template_name="index.html")),
    # re_path(r'^*',  TemplateView.as_view(template_name="index.html")),
    # # path('baton/', include('baton.urls')),
    # # path("", include("django_nextjs.urls")),
    # # path("leaveAndLicense/", TemplateView.as_view(template_name="leaveAndLicense.html")),
    # # path("leaveAndLicense/<str:uuid>/", TemplateView.as_view(template_name="leaveAndLicense/[licenseId].html")),
    # re_path(r"^$", TemplateView.as_view(template_name="index.html")),

    re_path('(^(?!(api|admin-api|user|employee-api|service-api|media)).*$)',TemplateView.as_view(template_name="index.html")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT) 

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# for route in react_routes:
#     urlpatterns += [
#         path('{}'.format(route), TemplateView.as_view(template_name='index.html'))
#     ]