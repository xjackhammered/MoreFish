from rest_framework import serializers

from assets.serializers import DistrictSerializers
from core.serializers import CorePaginationSerializer, CoreSerializer
from store.product.serializers import ProductSerializer

class OrderItemSerializer(CoreSerializer):
    order_item = ProductSerializer()
    order_price = serializers.IntegerField()
    quantity = serializers.IntegerField()

class OrderBillingAddressSerializer(serializers.Serializer):
    district = serializers.CharField()
    city = serializers.CharField()
    address_line_1 = serializers.CharField(allow_blank=True)
    address_line_2 = serializers.CharField(allow_blank=True)

class OrderShippingAddressSerializer(serializers.Serializer):
    district = serializers.CharField()
    city = serializers.CharField()
    address_line_1 = serializers.CharField(allow_blank=True)
    address_line_2 = serializers.CharField(allow_blank=True)
    

class OrderSerializer(CoreSerializer):
    orderitem_set = OrderItemSerializer(many=True,required=False)
    order_shipping_address = OrderShippingAddressSerializer()
    order_billing_address = OrderBillingAddressSerializer()

class OrderListSerializer(CorePaginationSerializer):
    data=OrderSerializer(many=True)    

class CreateOrderSerializer(serializers.Serializer):
    cart_guid = serializers.CharField()
    billing_address = OrderBillingAddressSerializer()
    shipping_address = OrderShippingAddressSerializer()