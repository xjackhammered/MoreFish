from django.contrib import admin
from .models import (
    PoultryFarm, Device, Sensor, SensorConfig, SensorReading,
    RawMQTTData, PoultryNotification, PoultryDeviceData
)


class SensorConfigInline(admin.TabularInline):
    model = SensorConfig
    extra = 0
    fields = ('sensor', 'multiplier', 'sensor_status')
    autocomplete_fields = ('sensor',)


class PoultryDeviceDataInline(admin.TabularInline):
    model = PoultryDeviceData
    extra = 0
    readonly_fields = ('sensor', 'value', 'data_time', 'updated_at')
    fields = ('sensor', 'value', 'data_time', 'updated_at')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'unit', 'min_value', 'max_value', 'icon')
    search_fields = ('name',)


@admin.register(PoultryFarm)
class PoultryFarmAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'company', 'location', 'created_at')
    search_fields = ('name', 'company__name')
    list_filter = ('company',)
    filter_horizontal = ('users',)


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'client_id', 'farm', 'company', 'dev_status', 'latest_reading_timestamp')
    search_fields = ('name', 'client_id')
    list_filter = ('dev_status', 'company')
    readonly_fields = ('latest_reading_timestamp', 'latest_reading_data', 'created_at', 'updated_at')
    inlines = [SensorConfigInline, PoultryDeviceDataInline]


@admin.register(SensorConfig)
class SensorConfigAdmin(admin.ModelAdmin):
    list_display = ('device', 'sensor', 'multiplier', 'sensor_status')
    search_fields = ('device__client_id', 'sensor__name')
    list_filter = ('sensor', 'sensor_status')
    autocomplete_fields = ('sensor',)


@admin.register(PoultryDeviceData)
class PoultryDeviceDataAdmin(admin.ModelAdmin):
    list_display = ('device', 'sensor', 'value', 'data_time', 'updated_at')
    search_fields = ('device__client_id', 'sensor__name')
    list_filter = ('sensor',)
    readonly_fields = ('device', 'sensor', 'value', 'data_time', 'created_at', 'updated_at')

    def has_add_permission(self, request):
        return False


@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    date_hierarchy = 'timestamp'
    search_fields = ('device__client_id', 'device__name')
    list_filter = ('device',)
    readonly_fields = ('created_at',)

    def get_list_display(self, request):
        base = ['id', 'device', 'timestamp']
        exclude = set(base + ['created_at'])
        model_fields = [
            f.name for f in self.model._meta.get_fields()
            if f.name not in exclude and not f.is_relation
        ]
        return base + sorted(model_fields)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('device')


@admin.register(RawMQTTData)
class RawMQTTDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'device', 'topic', 'received_at', 'payload')
    search_fields = ('device__client_id',)
    list_filter = ('device',)
    readonly_fields = ('received_at', 'payload')


@admin.register(PoultryNotification)
class PoultryNotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'device', 'sensor', 'value', 'urgency', 'is_read', 'notified_at')
    search_fields = ('device__client_id', 'sensor__name')
    list_filter = ('urgency', 'is_read', 'sensor')
    readonly_fields = ('notified_at',)
    actions = ['mark_as_read']

    @admin.action(description='Mark selected notifications as read')
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)