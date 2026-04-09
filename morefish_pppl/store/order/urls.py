from django.urls import path

from store.order.views import CreateOrder,OrderList
urlpatterns = [
    path('create/',CreateOrder.as_view()),
    path('list/',OrderList.as_view()),
]
