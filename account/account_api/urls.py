from django.urls import path
from .views import (
    RentalRegistration,
    FarmerRegisteration,
    InvestorLoginAPI,
    RentalLoginAPI,
    UserProfile,
    PasswordReset,
    ResetPasswordAPI,
    ChangePasswordView,
    RentalLoginRefreshAPI
)

urlpatterns = [
    path("password-reset-link/",PasswordReset.as_view(),name="request-password-reset",),
    path("password-reset/<str:encoded_pk>/<str:token>/",ResetPasswordAPI.as_view(),name="reset-password",),
    path("rental-register/",RentalRegistration.as_view(),name="user-register"),
    path("farmer-register/",FarmerRegisteration.as_view(),name="farmer-register"),
    path("profile-update/",UserProfile.as_view(),name="profile-update"),
    path("profile-get/",UserProfile.as_view(),name="profile-get"),
    path('change_password/', ChangePasswordView.as_view(), name='change_password'),
    path("investor-login/",InvestorLoginAPI.as_view(),name = "investor-login"),
    path("rental-login/",RentalLoginAPI.as_view(),name = "rental-login"),
    path("rental-logout/",RentalLoginRefreshAPI.as_view(),name = "rental-logout"),

    
]