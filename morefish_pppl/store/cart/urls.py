from django.urls import path

from store.cart.views import CartAddItem, DeleteCartItem, ViewCart

urlpatterns = [
    path('add/item/',CartAddItem.as_view()),
    path('view/',ViewCart.as_view()),
    path('delete/item/',DeleteCartItem.as_view())
]
