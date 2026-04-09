from django.urls import path
from .views import AppVersionList

urlpatterns = [
    path('versions/', AppVersionList.as_view(), name='appversion-list'),
]