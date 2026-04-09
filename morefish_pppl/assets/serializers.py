from rest_framework_jwt.settings import api_settings

from assets.models import AssetsType, AssetsProperties, District
from users.serializers import UserDetailSerializer, UserPhoneSerializer, UserAddressSerializer, CitizenshipSerializer, \
    EducationSerializer, OccupationSerializer, LocationSerializer, FCMSerializer, OTPSerializer

JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER
import json
from rest_framework import serializers
from users.models import User

class AssetsTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetsType
        fields = ('ast_title',)

class AssetsSerializer(serializers.ModelSerializer):
    ast_type = AssetsTypeSerializer()
    ast_user = UserDetailSerializer()
    ast_created_at = serializers.DateTimeField(format="%Y-%m-%d %I:%M:%S %p")
    class Meta:
        model = AssetsProperties
        fields = ('id', 'ast_name', 'ast_user', 'ast_type', 'ast_address', 'ast_lat', 'ast_long', 'ast_length', 'ast_width', 'ast_depth', 'ast_min_ph', 'ast_max_ph', 'ast_min_temp', 'ast_max_temp', 'ast_min_turbidity', 'ast_max_turbidity', 'ast_min_n', 'ast_max_n', 'ast_min_p', 'ast_max_p', 'ast_min_k', 'ast_max_k', 'ast_min_moisture', 'ast_max_moisture', 'ast_description', 'ast_image', 'ast_created_at')

class AssetsListSerializer(serializers.ModelSerializer):
    ast_type = AssetsTypeSerializer()
    ast_created_at = serializers.DateTimeField(format="%Y-%m-%d %I:%M:%S %p")
    class Meta:
        model = AssetsProperties
        fields = ('id', 'ast_name', 'ast_user', 'ast_type', 'ast_address', 'ast_lat', 'ast_long', 'ast_length', 'ast_width', 'ast_depth', 'ast_min_ph', 'ast_max_ph', 'ast_min_temp', 'ast_max_temp', 'ast_min_turbidity', 'ast_max_turbidity', 'ast_min_n', 'ast_max_n', 'ast_min_p', 'ast_max_p', 'ast_min_k', 'ast_max_k', 'ast_min_moisture', 'ast_max_moisture', 'ast_description', 'ast_image', 'ast_created_at')

class UserWiseAssetsListSerializer(serializers.ModelSerializer):
    assets_user = AssetsListSerializer(many=True)
    user_phone = UserPhoneSerializer()
    user_address = UserAddressSerializer()
    user_citizenship = CitizenshipSerializer()
    user_education = EducationSerializer(many=True)
    user_occupation = OccupationSerializer()
    user_location = LocationSerializer(many=True)

    class Meta:
        model = User
        fields = ['id', 'usr_email', 'first_name', 'last_name', 'is_active', 'user_type', 'user_phone', 'user_address',
                  'user_citizenship', 'user_education', 'user_occupation', 'user_location', 'assets_user',]
        
class AssetsManualSerializer(serializers.ModelSerializer):
   # ast_type = AssetsTypeSerializer()
   # ast_created_at = serializers.DateTimeField(format="%Y-%m-%d %I:%M:%S %p")
    class Meta:
        model = AssetsProperties
        fields = ('id', 'ast_name')

class DistrictSerializers(serializers.Serializer):
    district = serializers.CharField(required=False,allow_blank=True)