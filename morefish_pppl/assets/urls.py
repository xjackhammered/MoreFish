from django.conf import settings
from django.urls import path
from django.views.static import serve
#
from .views import AssetsList, SendMessageToOwner, AssetsAssignToUser, AssetsUserWiseList, AssetUnassetsAssignToUser, AssetsUnderUser, AssetsUnderUserForReport

urlpatterns = [
    path('list/', AssetsList.as_view()),
    path('user/wise/list/', AssetsUserWiseList.as_view()),
    path('assign/to/user/', AssetsAssignToUser.as_view()),
    path('unassign/to/user/', AssetUnassetsAssignToUser.as_view()),
    path('send/message/', SendMessageToOwner.as_view()),
    path('user/asset/list', AssetsUnderUser.as_view()),   
    path('user/report/', AssetsUnderUserForReport.as_view()),
]
