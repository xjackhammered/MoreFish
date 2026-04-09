import math
from os import path
from django.contrib import admin
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils.html import format_html
import pytz
# from device.forms import CalibrationForm, RawDataCalulationAdminForm
from assets.models import AssetsProperties
from device.models import (
    Complain,
    ComplainCategory,
    GatewayType,
    InvalidValue,
    DeviceGateway,
    Sensor,
    SensorConfiguration,
    TypeInformation,
    ModelInformation,
    DeviceData,
    # Sensor,
    Device,
    # ProblemDevices,
    Camera,
    DeviceRawData,
    TimeSchedule,
    DeviceControlInfo,
    UserManualData,
    Weather,
    WeatherReport,
    RetrievedCalibration
)
import datetime
from django.http import HttpResponse
from django.urls import reverse
from openpyxl import Workbook

from users.models import Company

class CustomAdminSite(admin.AdminSite):
    site_header = 'Custom Admin Site'
    site_title = 'Custom Admin Site'

    def get_urls(self):
        from .views import raw_data_calculation
        urls = super().get_urls()
        my_urls = [
            path('custom_admin/', self.admin_view(raw_data_calculation), name='custom_admin_view'),
        ]
        return my_urls + urls

class TimeScheduleAdmin(admin.StackedInline):
    model = TimeSchedule


class TypeInformationAdmin(admin.ModelAdmin):
    exclude = ["typ_created_by", "typ_created_at"]
    list_display = ("typ_title", "typ_created_at")

    def save_model(self, request, obj, form, change):
        if not obj.id:
            obj.typ_created_by = request.user
        if change and obj.id:
            obj.typ_created_by = request.user
        obj.save()


class ModelInformationAdmin(admin.ModelAdmin):
    exclude = ["mod_created_by", "typ_created_at"]
    list_display = ("mod_name", "mod_created_at")

    def save_model(self, request, obj, form, change):
        if not obj.id:
            obj.mod_created_by = request.user
        if change and obj.id:
            obj.mod_created_by = request.user
        obj.save()


class DeviceDataAdmin(admin.ModelAdmin):
    exclude = ["dvd_created_at", "dvd_updated_at"]
    list_display = (
        "dvd_val",
        "dvd_sen",
        "dvd_dev",
        "company",
        "dvd_created_at",
        "device_data_time"
    )
    list_filter = [
        "dvd_dev",
    ]
    
    

class DeviceAdmin(admin.ModelAdmin):
    exclude = ["dev_created_by", "dev_updated_by"]
    inlines = [
        TimeScheduleAdmin,
    ]
    list_display = (
        "dev_name",
        "dev_asset",
        "dev_status",
        "dev_serial_no",
    )

    search_fields = ("dev_name",)
    list_filter = ["dev_type", "dev_asset", "dev_status"]

    def save_model(self, request, obj, form, change):
        if not obj.id:
            obj.dev_created_by = request.user
            obj.dev_updated_by = request.user
        if change and obj.id:
            obj.dev_updated_by = request.user
        obj.save()


class DeviceGatewayAdmin(admin.ModelAdmin):
    exclude = ["dvg_created_by", "dvg_updated_by"]
    list_display = (
        "dvg_name",
        "dvg_assets",
        "dvg_protocol",
        "dvg_serial_no",
    )

    search_fields = (
        "dvg_name",
        "dvg_app",
    )
    list_filter = [
        "dvg_assets",
    ]

    def save_model(self, request, obj, form, change):
        if not obj.id:
            obj.dvg_created_by = request.user
            obj.dvg_updated_by = request.user
        if change and obj.id:
            obj.dvg_updated_by = request.user
        obj.save()

@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ["sensor_name"]
    
# @admin.register(SensorConfiguration)
# class SensorConfigurationAdmin(admin.ModelAdmin):
#     list_display = ["device",
#     "pid",
#     "address",
#     "sensor",
#     "multiplier"]
#
#     search_fields = ("device",)


@admin.register(SensorConfiguration)
class SensorConfigurationAdmin(admin.ModelAdmin):
    list_display = (
        "device_name",
        "sensor_name",
        "pid",
        "address",
        "multiplier",
        "sensor_status_display"
    )
    search_fields = (
        "device__dev_name",     # search by related device name
        "sensor__sensor_name",  # search by related sensor name
        "pid",
        "address",
    )
    list_filter = (
        "device",
        "sensor",
        "sensor_status",
    )
    list_select_related = ("device", "sensor")  # Optimize foreign key queries

    def device_name(self, obj):
        return obj.device.dev_name if obj.device else "—"
    device_name.short_description = "Device"

    def sensor_name(self, obj):
        return obj.sensor.sensor_name if obj.sensor else "—"
    sensor_name.short_description = "Sensor"

    def sensor_status_display(self, obj):
        return dict(SensorConfiguration._meta.get_field("sensor_status").choices).get(obj.sensor_status, "—")
    sensor_status_display.short_description = "Status"


class CameraAdmin(admin.ModelAdmin):
    exclude = ["cam_created_by", "cam_updated_by"]
    list_display = ("cam_assets", "cam_name", "cam_serial", "cam_ip", "cam_created_at")

    search_fields = ("cam_name",)
    list_filter = [
        "cam_assets",
    ]

    def save_model(self, request, obj, form, change):
        if not obj.id:
            obj.cam_created_by = request.user
            obj.cam_updated_by = request.user
        if change and obj.id:
            obj.cam_updated_by = request.user
        obj.save()


class DeviceRawDataAdmin(admin.ModelAdmin):
    list_display = ("drd_dev", "drd_data", "drd_created_at","device_data_time")
    list_filter = [
        "drd_dev",
    ]


class DeviceControlInfoAdmin(admin.ModelAdmin):
    list_display = ("dci_dev", "dci_data", "dci_created_at")
    list_filter = [
        "dci_dev",
    ]


class InvalidValueAdmin(admin.ModelAdmin):
    list_display = (
        "sensor",
        "max_invalid_value",
        "min_invalid_value"
    )


class WeatherReportAdmin(admin.ModelAdmin):
    list_display = (
        "dvd_dev",
        "weather_temperature",
        "weather_description",
        "weather_humidity",
        "weather_city",
        "weather_created_at",
    )


class GatewayTypeAdmin(admin.ModelAdmin):
    list_display = ["name"]


class WeatherAdmin(admin.ModelAdmin):
    list_display = (
        "weather_temperature",
        "weather_description",
        "weather_humidity",
        "weather_district",
        "weather_created_at",
        "sunlight_level",
        "solar_radiation"
    )
class ManualDataAdmin(admin.ModelAdmin):
    exclude = ["man_created_at"]
    list_display = (
        "man_assets",
        "man_ph",
        "man_tds",
        "man_temperature",
        "man_ammonia",
        "man_DO",
        "man_created_at",
        "man_updated_at",
        "man_created_by",
    )
    list_filter = [
        "man_created_by",
    ]
    def save_model(self, request, obj, form, change):
        if not obj.id:
            obj.man_created_at = request.user
            obj.man_updated_at = request.user
        if change and obj.id:
            obj.man_updated_at = request.user
        obj.save()


class ComplainCategoryAdmin(admin.ModelAdmin):
    list_display = (
        'category_name',
    )

class ComplainAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'complain_category',
        'complain_title',
        'complain_description',
        'complain_image',
        'complain_status',
        'complain_created_at',
    )


#
# from django.contrib import admin
# from django.http import HttpResponse
# from rangefilter.filters import DateRangeFilter
# from .models import DeviceDataHistory
# from assets.models import AssetsProperties  # Required for user-asset lookup
# import openpyxl
# from io import BytesIO
#
#
# @admin.register(DeviceDataHistory)
# class DeviceDataHistoryAdmin(admin.ModelAdmin):
#     list_display = (
#         'id', 'dvd_dev', 'dvd_dvg', 'dvd_sen', 'dvd_val',
#         'device_data_time', 'asset', 'company'
#     )
#
#     list_filter = (
#         ('device_data_time', DateRangeFilter),
#         'dvd_sen', 'dvd_dev', 'dvd_dvg', 'company', 'asset',
#     )
#
#     search_fields = (
#         'dvd_val',
#         'dvd_dev__name',
#         'dvd_sen__name',
#         'dvd_dvg__name',
#         'asset__ast_name',
#         'company__name',
#     )
#
#     actions = ['export_filtered_to_excel']
#     ordering = ('-device_data_time',)
#
#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         user = request.user
#
#         # Superuser sees all data
#         if user.is_superuser:
#             return qs
#
#         # Get all assets assigned to this user via the ManyToManyField
#         user_assets = AssetsProperties.objects.filter(ast_user=user)
#
#         # If no assets assigned, return no records
#         if not user_assets.exists():
#             return qs.none()
#
#         # Build filters
#         filters = {
#             'asset__in': user_assets,
#         }
#
#         # Optional: if user is associated with a company
#         if hasattr(user, 'company') and user.company:
#             filters['company'] = user.company
#
#         return qs.filter(**filters)
#
#     def export_filtered_to_excel(self, request, queryset):
#         # Fall back to filtered queryset if not explicitly passed
#         if not queryset.exists():
#             queryset = self.get_queryset(request)
#
#         workbook = openpyxl.Workbook()
#         worksheet = workbook.active
#         worksheet.title = 'Device Data History'
#
#         headers = [
#             'ID', 'Device', 'Gateway', 'Sensor', 'Value',
#             'Device Data Time', 'Asset', 'Company'
#         ]
#         worksheet.append(headers)
#
#         for obj in queryset:
#             worksheet.append([
#                 obj.id,
#                 str(obj.dvd_dev) if obj.dvd_dev else '',
#                 str(obj.dvd_dvg) if obj.dvd_dvg else '',
#                 str(obj.dvd_sen) if obj.dvd_sen else '',
#                 obj.dvd_val or '',
#                 obj.device_data_time.strftime("%Y-%m-%d %H:%M:%S") if obj.device_data_time else '',
#                 str(obj.asset) if obj.asset else '',
#                 str(obj.company) if obj.company else '',
#             ])
#
#         output = BytesIO()
#         workbook.save(output)
#         output.seek(0)
#
#         response = HttpResponse(
#             output.read(),
#             content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
#         )
#         response['Content-Disposition'] = 'attachment; filename=device_data_filtered_export.xlsx'
#         return response
#
#     export_filtered_to_excel.short_description = "Export filtered data to Excel"


from django.http import HttpResponse
from rangefilter.filters import DateRangeFilter
from django.contrib import admin
from .models import DeviceDataHistory, AeratorCommandLog
import openpyxl
from io import BytesIO

@admin.register(DeviceDataHistory)
class DeviceDataHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'dvd_dev', 'dvd_dvg', 'dvd_sen', 'dvd_val',
        'dvd_created_at', 'asset', 'company'
    )

    list_filter = (
        ('dvd_created_at', DateRangeFilter),
        'dvd_sen', 'dvd_dev', 'dvd_dvg', 'company', 'asset',
    )

    search_fields = (
        'dvd_val',
        'dvd_dev__name',
        'dvd_sen__name',
        'dvd_dvg__name',
        'asset__ast_name',
        'company__name',
    )

    actions = ['export_filtered_to_excel']
    ordering = ('-dvd_created_at',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user

        if user.is_superuser:
            return qs

        # Correct field: 'id' not 'ast_id'
        user_asset_ids = AssetsProperties.objects.filter(ast_user=user).values_list('id', flat=True)

        if not user_asset_ids:
            return qs.none()

        filters = {'asset_id__in': user_asset_ids}

        if hasattr(user, 'company') and user.company:
            filters['company'] = user.company

        return qs.filter(**filters)

    def export_filtered_to_excel(self, request, queryset):
        if not queryset.exists():
            queryset = self.get_queryset(request)

        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        worksheet.title = 'Device Data History'

        headers = [
            'ID', 'Device', 'Gateway', 'Sensor', 'Value',
            'Device Data Time', 'Asset', 'Company'
        ]
        worksheet.append(headers)

        for obj in queryset:
            worksheet.append([
                obj.id,
                str(obj.dvd_dev) if obj.dvd_dev else '',
                str(obj.dvd_dvg) if obj.dvd_dvg else '',
                str(obj.dvd_sen) if obj.dvd_sen else '',
                obj.dvd_val or '',
                obj.dvd_created_at.strftime("%Y-%m-%d %H:%M:%S") if obj.dvd_created_at else '',
                str(obj.asset) if obj.asset else '',
                str(obj.company) if obj.company else '',
            ])

        output = BytesIO()
        workbook.save(output)
        output.seek(0)

        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename=device_data_filtered_export.xlsx'
        return response

    export_filtered_to_excel.short_description = "Export filtered data to Excel"



from .models import Aerator, AeratorStatusLog

@admin.register(Aerator)
class AeratorAdmin(admin.ModelAdmin):
    list_display = (
        'device',
        'aerator_id',
        'aerator_name',
        'mqtt_client_id',
        'is_running',
        'is_active',
        'updated_at',
    )
    # fields = (
    #     'device',
    #     'aerator_id',
    #     'aerator_name',
    #     'mqtt_client_id',
    #     'is_running',
    #     'is_active',
    # )
    list_filter = (
        'device',
        'is_running',
        'is_active',
    )
    search_fields = (
        'device__dev_name',
        'aerator_id',
        'aerator_name',
        'mqtt_client_id',
    )
    ordering = (
        'device__dev_name',
        'aerator_id',
    )
    list_select_related = (
        'device',
    )

@admin.register(AeratorStatusLog)
class AeratorStatusLogAdmin(admin.ModelAdmin):
    list_display = (
        'aerator',
        'was_running',
        'timestamp',
    )
    list_filter = (
        'aerator__device',
        'was_running',
    )
    search_fields = (
        'aerator__device__dev_name',
        'aerator__aerator_id',
    )
    date_hierarchy = 'timestamp'
    ordering = (
        '-timestamp',
    )
    list_select_related = (
        'aerator',
        'aerator__device',
    )
    raw_id_fields = (
        'aerator',
    )



@admin.register(AeratorCommandLog)
class AeratorCommandLogAdmin(admin.ModelAdmin):
    list_display = (
        'aerator',
        'command_on',
        'sent_at',
        'acked',
        'acked_at',
    )
    list_filter = (
        'command_on',
        'acked',
        'aerator__device',
    )
    search_fields = (
        'aerator__device__dev_name',
        'aerator__mqtt_id',
    )
    date_hierarchy = 'sent_at'
    ordering = (
        '-sent_at',
    )
    list_select_related = (
        'aerator',
        'aerator__device',
    )
    raw_id_fields = (
        'aerator',
    )



admin.site.register(DeviceData, DeviceDataAdmin)
admin.site.register(TypeInformation, TypeInformationAdmin)
admin.site.register(ModelInformation, ModelInformationAdmin)
admin.site.register(Device, DeviceAdmin)
admin.site.register(Camera, CameraAdmin)
admin.site.register(DeviceRawData, DeviceRawDataAdmin)
admin.site.register(DeviceControlInfo, DeviceControlInfoAdmin)
admin.site.register(WeatherReport, WeatherReportAdmin)
admin.site.register(GatewayType, GatewayTypeAdmin)
admin.site.register(InvalidValue, InvalidValueAdmin)
admin.site.register(Weather, WeatherAdmin)
admin.site.register(DeviceGateway, DeviceGatewayAdmin)
admin.site.register(UserManualData, ManualDataAdmin)
admin.site.register(ComplainCategory, ComplainCategoryAdmin)
admin.site.register(Complain, ComplainAdmin)
