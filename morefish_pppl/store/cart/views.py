import logging
from django.http import HttpRequest
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from core.schema import generate_response_schema
from store.cart.models import Cart, CartItem
from store.cart.serializers import CartAddItemSerializer, CartSerializer
from store.product.models import Product
from django.db.models import Prefetch
from django.db import transaction

logger = logging.getLogger("__name__")
logger.setLevel(logging.ERROR)

class ViewCart(APIView):
    permission_classes = [AllowAny]
    serializer_class = CartSerializer
    
    def get(self,request:HttpRequest):
        session_id = request.session.session_key
        try:
            cart = Cart.objects.prefetch_related(Prefetch("cartitem_set",queryset=CartItem.objects.select_related('product').filter(is_deleted=False))).get(is_deleted=False,session_id=session_id)
            cart_serializer = CartSerializer(cart)
            print("CART EXISTS")
            return Response({
                "data":cart_serializer.data,
                "status_code":status.HTTP_200_OK,
                "success":"True"
            })
        except Cart.DoesNotExist:
            return Response(
                {
                "data":{},
                "status_code":status.HTTP_404_NOT_FOUND,
                "success":"True",
                "message":"Cart is Empty"
            }
            )
# Create your views here.
class CartAddItem(APIView):
    permission_classes = [AllowAny]
    serializer_class = CartAddItemSerializer
    
    def post(self,request:HttpRequest):
        session_id = request.session.session_key
        cart_serializer = self.serializer_class(data=request.data)
        try:
            cart_serializer.is_valid(raise_exception=True)
        except Exception as e:
            logger.error(f"Error {e}")
            return Response({
                "message":f"Validation Error {e}",
                "status_code":status.HTTP_406_NOT_ACCEPTABLE,
                "success":"False"
            })
        try:
            product = Product.objects.get(guid=request.data['product_guid'])
        except Product.DoesNotExist:
            return Response({
                "message":"Invalid product ID",
                "status_code":status.HTTP_404_NOT_FOUND,
                "success":"False"
            })
        try:
            cart = Cart.objects.get(is_deleted=False,session_id=session_id)
        except Cart.DoesNotExist:
            with transaction.atomic():
                cart = Cart.objects.create(session_id=session_id)
        try:
            cart_item = CartItem.objects.get(cart_id=cart.id,product_id=product.id,is_deleted=False)
            print("CART ITME EXISTS")
            with transaction.atomic():
                cart_item.quantity += 1
                cart_item.price += product.price
                cart_item.save()
        except CartItem.DoesNotExist:
            with transaction.atomic():
                cart_item = CartItem.objects.create(cart_id=cart.id,product_id=product.id,price=product.price,quantity=1)
        
        return Response({
            "message":"Product Added to cart",
            "status_code":status.HTTP_201_CREATED,
            "success":"True",
        })
        
class DeleteCartItem(APIView):
    permission_classes = [AllowAny]
    
    def delete(self,request:HttpRequest):
        """Delete item from cart

        Parameters:
            - cart_item_guid: str
        """
        cart_item_guid = request.GET.get('cart_item_guid',None)
        
        try:
            cart_item = CartItem.objects.get(guid=cart_item_guid,is_deleted=False)
        except CartItem.DoesNotExist:
            return Response({
                "message":"Invalid Cart Item Guid",
                "status_code":status.HTTP_404_NOT_FOUND,
                "success":"True"
            })
        with transaction.atomic():
            if cart_item.quantity>1:
                product = Product.objects.get(id=cart_item.product.id)
                print("CART ITEM QUANTITY >1")
                cart_item.quantity-=1
                cart_item.price-=product.price
                cart_item.save()
            else:
                cart_item.is_deleted=True
                cart_item.save()
        cart = Cart.objects.prefetch_related("cartitem_set").get(id=cart_item.cart_id)
        print(cart.cartitem_set)
        check_if_any_cartitems_in_cart = CartItem.objects.filter(cart_id=cart.id,is_deleted=False).exists()
        if not check_if_any_cartitems_in_cart:
            print("DELETING CART")
            with transaction.atomic():
                cart.is_deleted=True
                cart.save()
        return Response({
            "message":"Item Removed From cart",
            "status_code":status.HTTP_204_NO_CONTENT,
            "success":"True"
        })