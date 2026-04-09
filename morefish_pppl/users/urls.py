from django.conf import settings
from django.urls import path
from django.views.static import serve
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token

from .views import CompanyList, CompanySelector, Login, RefreshToken, Register, Logout, UserList, UserDetails, ChangePassword, FcmTokenUpdate, ForgotPassword, \
    OtpVerify, ResetPassword, UserActiveInactive, ResendOtp, DeleteUser, OtpSend, ExistingUserCheck

urlpatterns = [
    # path('api/logout/', Logout.as_view(), name='Logout'),
    path('login/', Login.as_view()),
    path('refresh_token/', RefreshToken.as_view()),
    path('registration/', Register.as_view()),
    path('logout/', Logout.as_view()),
    path('user/list/', UserList.as_view()),
    path('user/active/inactive/', UserActiveInactive.as_view()),
    path('user/details/<int:pk>/', UserDetails.as_view()),
    path('user/password/change/', ChangePassword.as_view()),
    path('user/forgot/password/', ForgotPassword.as_view()),
    path('user/otp/verify/', OtpVerify.as_view()),
    path('user/existing/check/', ExistingUserCheck.as_view()),
    path('user/otp/resend/', ResendOtp.as_view()),
    path('user/otp/send/', OtpSend.as_view()),
    path('user/delete/', DeleteUser.as_view()),
    path('user/reset/password/', ResetPassword.as_view()),
    path('user/fcm/token/update/', FcmTokenUpdate.as_view()),
    path('user/company/set/',CompanySelector.as_view()),
    path('company/list',CompanyList.as_view())
]
