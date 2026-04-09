from rest_framework import serializers
from core.serializers import CoreSerializer
from store.product.serializers import ProductSerializer

class CartAddItemSerializer(serializers.Serializer):
    product_guid = serializers.CharField()

class CartItemSerializer(CoreSerializer):
    product = ProductSerializer(many=False)
    price = serializers.IntegerField()
    quantity= serializers.IntegerField()
    
class CartSerializer(CoreSerializer):
    cartitem_set = CartItemSerializer(many=True,required=False)