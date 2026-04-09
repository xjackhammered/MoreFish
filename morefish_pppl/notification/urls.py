from django.conf import settings
from django.urls import path
from django.views.static import serve
#
from .views import UserWiseDateWiseNotificationList, UserWiseDeviceWiseNotificationHistory, UserWiseDeviceWiseNotificationList, UserWiseYesterdayNotificationList, UserWiseTodayNotificationList, \
    UserWiseNotificationList, UserWiseNotificationHistory

urlpatterns = [
    path('all/list/<int:user_id>/', UserWiseNotificationList.as_view()),
    path('today/list/<int:user_id>/', UserWiseTodayNotificationList.as_view()),
    path('yesterday/list/<int:user_id>/', UserWiseYesterdayNotificationList.as_view()),
    path('date_wise/list/<int:user_id>/', UserWiseDateWiseNotificationList.as_view()),
    path('history/', UserWiseNotificationHistory.as_view()),
    path('all/pond/list/', UserWiseDeviceWiseNotificationList.as_view()),
    path("device/wise/history/", UserWiseDeviceWiseNotificationHistory.as_view()),
]
