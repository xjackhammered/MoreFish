from rest_framework import serializers
from .models import (
    Device, PoultryFarm, Sensor, SensorConfig, SensorReading,
    PoultryNotification, PoultryDeviceData
)


# ─── SENSOR (template) ───────────────────────────────────────────────────────
class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = ['id', 'name', 'unit', 'min_value', 'max_value', 'min_invalid', 'max_invalid', 'icon']


# ─── SENSOR CONFIG ───────────────────────────────────────────────────────────
class SensorConfigSerializer(serializers.ModelSerializer):
    sensor_details = SensorSerializer(source='sensor', read_only=True)
    sensor_status_display = serializers.CharField(source='get_sensor_status_display', read_only=True)

    class Meta:
        model = SensorConfig
        fields = [
            'id', 'sensor', 'sensor_details', 'multiplier',
            'sensor_status', 'sensor_status_display',
        ]


# ─── LIVE SENSOR VALUE (dashboard) ───────────────────────────────────────────
class SensorLiveValueSerializer(serializers.Serializer):
    sensor_id     = serializers.IntegerField()
    name          = serializers.CharField()
    unit          = serializers.CharField(allow_blank=True)
    last_value    = serializers.CharField()       # value or "No data received yet"
    danger_status = serializers.CharField()       # "perfect" | "danger" | "invalid"
    data_time     = serializers.CharField(allow_blank=True)
    sensor_status = serializers.IntegerField()


class DeviceDashboardSerializer(serializers.Serializer):
    device_id     = serializers.IntegerField()
    device_name   = serializers.CharField()
    device_status = serializers.CharField()
    client_id     = serializers.CharField()
    sensors       = SensorLiveValueSerializer(many=True)


class FarmDashboardSerializer(serializers.Serializer):
    farm_id   = serializers.IntegerField()
    farm_name = serializers.CharField()
    device    = DeviceDashboardSerializer(required=False, allow_null=True)


# ─── FARM LIST ───────────────────────────────────────────────────────────────
class PoultryFarmListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PoultryFarm
        fields = ('id', 'name', 'location')


# ─── DEVICE DETAIL ───────────────────────────────────────────────────────────
class DeviceDetailSerializer(serializers.ModelSerializer):
    farm_name = serializers.CharField(source='farm.name', read_only=True, default='')
    status_label = serializers.SerializerMethodField()
    sensor_configs = SensorConfigSerializer(many=True, read_only=True)

    class Meta:
        model = Device
        fields = (
            'id', 'client_id', 'name', 'location',
            'dev_status', 'status_label',
            'farm_name', 'sensor_configs',
            'latest_reading_timestamp', 'latest_reading_data',
        )

    def get_status_label(self, obj):
        return {0: 'Offline', 1: 'Online', 2: 'Problem'}.get(obj.dev_status, 'Unknown')


# ─── LATEST READING (simple list view) ───────────────────────────────────────
class DeviceLatestReadingSerializer(serializers.ModelSerializer):
    latest_reading = serializers.SerializerMethodField()
    farm_name = serializers.CharField(source='farm.name', read_only=True, default='')

    class Meta:
        model = Device
        fields = ('id', 'client_id', 'name', 'location', 'farm_name', 'latest_reading')

    def get_latest_reading(self, obj):
        if obj.latest_reading_data:
            return {'timestamp': obj.latest_reading_timestamp, 'data': obj.latest_reading_data}
        return None


# ─── CHART DATA ───────────────────────────────────────────────────────────────
class SensorChartDataSerializer(serializers.Serializer):
    farm_id     = serializers.IntegerField()
    farm_name   = serializers.CharField()
    sensor_name = serializers.CharField()
    unit        = serializers.CharField(allow_blank=True)
    sensor_val  = serializers.ListField(child=serializers.CharField())
    time        = serializers.ListField(child=serializers.CharField())
    date_time   = serializers.CharField(allow_blank=True)


# ─── QUERY PARAM VALIDATORS ──────────────────────────────────────────────────
class FarmIdParamSerializer(serializers.Serializer):
    farm_id = serializers.IntegerField(required=True)


class ChartQuerySerializer(serializers.Serializer):
    farm_id    = serializers.IntegerField(required=True)
    sensor_key = serializers.CharField(required=True)   # now the sensor name (e.g., "temperature")
    type       = serializers.ChoiceField(
        choices=['daily', 'weekly', 'monthly', 'half-yearly', 'yearly'],
        default='daily'
    )


# ─── SENSOR READING (raw history) ────────────────────────────────────────────
class SensorReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorReading
        fields = (
            'id', 'timestamp',
            'temperature', 'ref_temperature', 'humidity',
            'light_intensity', 'nh3_gas', 'tvoc',
            'co2', 'aqi', 'pm25', 'pm10', 'sound_db',
        )


# ─── NOTIFICATIONS ───────────────────────────────────────────────────────────
class PoultryNotificationSerializer(serializers.ModelSerializer):
    sensor_name = serializers.CharField(source='sensor.name', read_only=True)

    class Meta:
        model = PoultryNotification
        fields = (
            'id', 'sensor', 'sensor_name',
            'value', 'urgency', 'message',
            'is_read', 'notified_at',
        )