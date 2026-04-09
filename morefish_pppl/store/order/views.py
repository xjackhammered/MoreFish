import logging
from django.http import HttpRequest
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from core.schema import generate_response_schema
from store.cart.models import Cart
from store.order.models import Order, OrderBillingAddress, OrderItem, OrderShippingAddress
from store.order.serializers import CreateOrderSerializer, OrderListSerializer, OrderSerializer
from store.product.models import Product
from django.db.models import Prefetch
from django.db import transaction
from django.core.paginator import Paginator
# Create your views here.

class CreateOrder(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreateOrderSerializer
    
    def post(self,request:HttpRequest):
        print(request.data["cart_guid"])
        cart_serializer = self.serializer_class(data=request.data)
        try:
            cart_serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({
                "message":f"Invalid request data {e}",
                "status_code":status.HTTP_406_NOT_ACCEPTABLE,
                "success":"False"
            })
        with transaction.atomic():
            billing_address = OrderBillingAddress.objects.create(
                district = request.data["billing_address"]["district"],
                city = request.data["billing_address"]["city"],
                address_line_1=request.data["billing_address"]["address_line_1"],
                address_line_2 =request.data["billing_address"]["address_line_2"]
            )
            
            shipping_address = OrderShippingAddress.objects.create(
                district = request.data["shipping_address"]["district"],
                city = request.data["shipping_address"]["city"],
                address_line_1=request.data["shipping_address"]["address_line_1"],
                address_line_2 =request.data["shipping_address"]["address_line_2"]
            )
            
        try:
            cart = Cart.objects.prefetch_related("cartitem_set").get(guid=request.data["cart_guid"],is_deleted=False)
        except Cart.DoesNotExist:
            return Response({
                "message":"Invalid cart guid",
                "status_code":status.HTTP_406_NOT_ACCEPTABLE,
                "success":"False"
            })
        order_items = []
        with transaction.atomic():
            order = Order.objects.create(
                user_id = request.user.id,
                order_status=1,
                shipping_address_id=shipping_address.id,
                billing_address_id = billing_address.id
            )
        for cart_item in cart.cartitem_set.all():
            order_item = OrderItem(
                order_id = order.id,
                order_item_id = cart_item.product.id,
                order_price = cart_item.price,
                quantity=cart_item.quantity
            )
            order_items.append(order_item)
        with transaction.atomic():
            created_order_items = OrderItem.objects.bulk_create(order_items)
            cart.is_deleted=True
            cart.save()
        return Response({
            "message":"Order Successfully Created",
            "success":"True",
            "status_code":status.HTTP_201_CREATED
        })
        
class OrderList(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    
    def get(self,request:HttpRequest):
        """ Order List

        Parameters:
            - page_number: int
            - size: size
        """
        
        page_number = request.GET.get('page_number',1)
        size = request.GET.get('size',25)
        
        order_queryset = Order.objects.prefetch_related("orderitem_set").select_related('billing_address','shipping_address').filter(is_deleted=False)
        paginated_queryset = Paginator(order_queryset,per_page=size)
        
        serialized_order = OrderSerializer(paginated_queryset.page(number=page_number).object_list,many=True)
        
        paginated_order_list = OrderListSerializer(
            data={
                "page_number": page_number,
                "total_items": paginated_queryset.count,
                "total_pages": paginated_queryset.num_pages,
                "has_next": paginated_queryset.page(number=page_number).has_next(),
                "has_prev": paginated_queryset.page(number=page_number).has_previous(),
                "page_size": size,
                "data": serialized_order.data,
            }
        )
        
        return Response({
            "message":"Order List",
            "status_code":status.HTTP_200_OK,
            "data":paginated_order_list.data,
            "success":"True"
        })
        