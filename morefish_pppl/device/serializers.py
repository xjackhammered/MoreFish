import datetime
from decimal import Decimal
from math import floor
from typing import OrderedDict
from rest_framework_jwt.settings import api_settings

from assets.models import AssetsProperties
from assets.serializers import AssetsSerializer, DistrictSerializers
from device.models import (
    Device,
    DeviceData,
    DeviceGateway,
    InvalidValue,
    TypeInformation,
    ModelInformation,
    Camera,
    Weather,
    UserManualData,
    Aerator,
)


JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER

from rest_framework import serializers


class AeratorInfoSerializer(serializers.ModelSerializer):
    aerator_pk = serializers.IntegerField(source='pk')
    aerator_name = serializers.CharField()
    aerator_id = serializers.CharField()
    is_running = serializers.BooleanField()

    class Meta:
        model = Aerator
        fields = ('aerator_pk', 'aerator_name', 'aerator_id', 'is_running')


class DeviceSerializer(serializers.ModelSerializer):
    dev_asset = AssetsSerializer(read_only=True)
    # device_data = DeviceDataSerializer(read_only=True, many=True)
    aerators = AeratorInfoSerializer(many=True, read_only=True)

    class Meta:
        model = Device
        fields = (
            "id",
            "dev_name",
            "dev_asset",
            "dev_protocol",
            "dev_location",
            "dev_lat",
            "dev_long",
            "dev_sim_no",
            "dev_serial_no",
            "dev_status",
            "dev_ip",
            "dev_mac",
            "dev_image",
            "aerators",
        )


class WeatherSerializer(serializers.Serializer):
    weather_temperature = serializers.SerializerMethodField(required=False)
    weather_humidity = serializers.SerializerMethodField(required=False)
    sunlight_level = serializers.CharField(required=False,allow_blank=True)
    solar_radiation = serializers.CharField(required=False,allow_blank=True)
    weather_district = DistrictSerializers(many=False,required=False)
    weather_temperature = serializers.CharField(required=False,allow_blank=True)
    weather_humidity = serializers.CharField(required=False,allow_blank=True)
    weather_description = serializers.CharField(required=False,allow_blank=True)

    def get_weather_temperature(self, obj):
        try:
            rounded_temperature = floor(obj.weather_temperature)
            print("FOUND TEMP ---------->",f"{rounded_temperature}°C")
            return f"{rounded_temperature}°C"
        except AttributeError:
            return ""

    def get_weather_humidity(self, obj):
        try:
            rounded_humidity = floor(obj.weather_humidity)
            return f"{rounded_humidity}%"
        except AttributeError:
            return ""
class DeviceDataSerializer(serializers.ModelSerializer):
    dvd_created_at = serializers.DateTimeField(format="%Y-%m-%d %I:%M:%S %p")
    # dvd_dev = DeviceSerializer(read_only=True)

    class Meta:
        model = DeviceData
        fields = (
            "dvd_status",
            "dvd_ph",
            "dvd_tds",
            "dvd_temp",
            "dvd_created_at",
            "dvd_dev",
        )


class CameraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = ("cam_name", "cam_brand", "cam_serial", "cam_ip", "cam_url")


class AssetsCameraSerializer(serializers.ModelSerializer):
    camera_asset = CameraSerializer(many=True)

    class Meta:
        model = AssetsProperties
        fields = (
            "id",
            "ast_name",
            "camera_asset",
        )





class UserManualDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserManualData
        fields = ('man_assets', 'man_ph', 'man_ammonia', 'man_DO', 'man_tds', 'man_temperature', 'man_created_by', 'man_created_at', 'man_updated_at') 
         
         
class SensorDataSerializer(serializers.Serializer):
    sensor_id = serializers.CharField()
    sensor_name = serializers.CharField()
    last_value = serializers.CharField()
    sensor_unit = serializers.CharField(required=False,allow_blank=True)
    danger_status = serializers.CharField(required=False,allow_blank=True)
    sensor_icon = serializers.CharField(required=False,allow_blank=True)
    data_time = serializers.CharField(required=False,allow_blank=True)
    sensor_status = serializers.CharField()

class DeviceDataSerializer(serializers.Serializer):
    device_id = serializers.CharField()
    device_name = serializers.CharField()
    device_status = serializers.CharField()
    sensors = SensorDataSerializer(many=True,required=False)
    aerators = AeratorInfoSerializer(many=True, required=False)  # ← ADD THIS

class AssetDataSerializer(serializers.Serializer):
    asset_id = serializers.CharField()
    weather = WeatherSerializer(many=False,required=False)
    asset_name = serializers.CharField()
    devices = DeviceDataSerializer(many=True,required=False)
    
    
class ResultDataSerializer(serializers.Serializer):
    result_data = AssetDataSerializer(required=False)


class PondDataSerializer(serializers.Serializer):
    asset_id = serializers.IntegerField(required=True, help_text="The ID of the asset")


class AeratorCommandSerializer(serializers.Serializer):
    aerator_id = serializers.CharField(max_length=64, required=True)
    command = serializers.IntegerField(
        min_value=0,
        max_value=1,
        help_text='0 = OFF, 1 = ON'
    )

