from rest_framework import serializers
from core.serializers import CorePaginationSerializer, CoreSerializer
from store.product.models import ProductCompany


class CategorySerializer(CoreSerializer):
    category_name = serializers.CharField()
    category_image = serializers.ImageField()


class ProductImageSerializer(CoreSerializer):
    image = serializers.ImageField()


# class ProductSerializer(CoreSerializer):
#     name = serializers.CharField()
#     description = serializers.CharField(allow_blank=True)
#     price = serializers.IntegerField()
#     productimage_set = ProductImageSerializer(many=True, required=False)


# Updated ProductSerializer includes the category details.
class ProductSerializer(CoreSerializer):
    name = serializers.CharField()
    description = serializers.CharField(allow_blank=True)
    # price = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    # Nest the category serializer to include its details:
    category = CategorySerializer(required=False)
    productimage_set = ProductImageSerializer(many=True, required=False)


class ProductSpecificationSerializer(CoreSerializer):
    specification = serializers.CharField()


class ProductDetailsSerializer(CoreSerializer):
    name = serializers.CharField()
    description = serializers.CharField(allow_blank=True)
    # price = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    productimage_set = ProductImageSerializer(many=True, required=False)
    productspecifications_set = ProductSpecificationSerializer(many=True, required=False)
    category = CategorySerializer(required=False)


class ProductListSerializer(CorePaginationSerializer):
    data = ProductSerializer(many=True)


# New serializer for ProductCompany based on your CoreSerializer:
# class ProductCompanySerializer(CoreSerializer):
#     id = serializers.IntegerField()
#     name = serializers.CharField()


class ProductCompanySerializer(CoreSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    company_image = serializers.ImageField()  # This field returns the image URL

    class Meta:
        model = ProductCompany
        fields = ['id', 'name', 'company_image']
