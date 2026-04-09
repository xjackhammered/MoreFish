import datetime
import json
import re
import traceback
import django
from django.db import models
from django.db.models import Q
# Create your models here.
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.forms import model_to_dict
from django.utils.translation import gettext_lazy as _
from pytz import timezone

from notification.models import Configuration, NotificationThreshold, Notifications

from django.db import transaction

from django.core.validators import MaxValueValidator, MinValueValidator

def current_date_time():
    bd_timezone = timezone('Asia/Dhaka')
    bd_time = datetime.datetime.now(bd_timezone)
    # time_stamp = bd_time.strftime('%Y-%m-%d %H:%M:%S')
    # print(time_stamp)
    return bd_time


class TypeInformation(models.Model):
    typ_title = models.TextField(blank=False, null=False)
    typ_created_at = models.DateTimeField(auto_now=True)
    typ_created_by = models.ForeignKey(
        'users.User',
        related_name="type_created_by",
        on_delete=models.SET_NULL, blank=True, null=True
    )

    class Meta:
        verbose_name = 'Device Type'
        verbose_name_plural = 'Device Types'

    def __str__(self):
        return "%s" % self.typ_title


class ModelInformation(models.Model):
    mod_name = models.TextField(blank=False, null=False)
    mod_created_at = models.DateTimeField(auto_now=True)
    mod_created_by = models.ForeignKey(
        'users.User',
        related_name="model_created_by",
        on_delete=models.SET_NULL, blank=True, null=True
    )

    class Meta:
        verbose_name = 'Device Model'
        verbose_name_plural = 'Device Models'

    def __str__(self):
        return "%s" % self.mod_name


class GatewayType(models.Model):
    name = models.TextField(max_length=150,null=True,blank=True)

    def __str__(self):
        return self.name
    
is_gateway_status = (
    (0, 'Offline'),
    (1, 'Online'),
    (2, 'Problem'),
)


class DeviceGateway(models.Model):
    class Meta:
        verbose_name = 'Gateway'
        verbose_name_plural = 'Gateways'
    
    dvg_name = models.CharField(max_length=200, null=True, blank=True)
    dvg_type = models.ForeignKey(TypeInformation, related_name='device_type', on_delete=models.SET_NULL, null=True,
                                 blank=True)
    dvg_protocol = models.CharField(max_length=200, blank=True, null=True)
    dvg_location = models.TextField(blank=True, null=True)
    dvg_lat = models.CharField(max_length=200, null=True, blank=True)
    dvg_long = models.CharField(max_length=200, null=True, blank=True)
    dvg_model = models.ForeignKey(ModelInformation, related_name='device_gateway_model', on_delete=models.SET_NULL,
                                  null=True, blank=True)
    dvg_sim_no = models.CharField(max_length=255, blank=True, null=True)
    dvg_serial_no = models.CharField(max_length=200, blank=True, null=True)
    dvg_ip = models.GenericIPAddressField(protocol='both', unpack_ipv4=False, blank=True, null=True)
    dvg_mac = models.CharField(max_length=200, blank=True, null=True)
    dvg_image = models.ImageField(upload_to='uploads/device_gateway/images/', blank=True, null=True)
    dvg_description = models.TextField(blank=True, null=True)
    dvg_assets = models.ForeignKey('assets.AssetsProperties', related_name='device_gateway_asset', blank=True,
                                   null=True, on_delete=models.SET_NULL)
    # dvg_app = models.OneToOneField('application.Application', related_name='device_app', on_delete=models.SET_NULL,
    #                                null=True, blank=True)
    company = models.ForeignKey("users.Company",null=True,blank=True, on_delete=models.SET_NULL)    
    is_deleted = models.BooleanField(default=False,
                                     help_text=('Designates whether this application is deleted'))
    dvg_created_at = models.DateTimeField(auto_now_add=True)
    dvg_updated_at = models.DateTimeField()
    dvg_created_by = models.ForeignKey(
        'users.User',
        related_name="device_gateway_created_by",
        on_delete=models.SET_NULL, blank=True, null=True
    )
    dvg_updated_by = models.ForeignKey(
        'users.User',
        related_name="device_gateway_updated_by",
        on_delete=models.SET_NULL, blank=True, null=True
    )
    dvg_model_type = models.ForeignKey("device.GatewayType",null=True,blank=True,on_delete=models.SET_NULL)
    gateway_status = models.IntegerField(choices=is_gateway_status, default=0, null=True, blank=True)
    def __str__(self):
        return "%s" % self.dvg_name


is_device_status = (
    (0, 'Offline'),
    (1, 'Online'),
    (2, 'Problem'),
)


class Device(models.Model):
    dev_name = models.CharField(max_length=200, null=True, blank=True)
    dev_dvg = models.ForeignKey(DeviceGateway, related_name='gateway_devices', on_delete=models.SET_NULL, null=True,
                                blank=True)
    dev_asset = models.OneToOneField('assets.AssetsProperties', related_name='device_asset', blank=True, null=True,
                                   on_delete=models.SET_NULL)
    dev_protocol = models.CharField(max_length=200, blank=True, null=True)
    dev_location = models.TextField(blank=True, null=True)
    dev_lat = models.CharField(max_length=200, null=True, blank=True)
    dev_long = models.CharField(max_length=200, null=True, blank=True)
    dev_model = models.ForeignKey(ModelInformation, related_name='device_model', on_delete=models.SET_NULL, null=True,
                                  blank=True)
    dev_type = models.ForeignKey(TypeInformation, related_name='device_types', on_delete=models.SET_NULL, null=True,
                                 blank=True)
    dev_sim_no = models.CharField(max_length=255, blank=True, null=True)
    dev_serial_no = models.CharField(max_length=200, blank=True, null=True)
    dev_ip = models.GenericIPAddressField(protocol='both', unpack_ipv4=False, blank=True, null=True)
    dev_mac = models.CharField(max_length=200, blank=True, null=True)
    dev_image = models.ImageField(upload_to='uploads/device/images/', blank=True, null=True)
    dev_description = models.TextField(blank=True, null=True)
    dev_status = models.IntegerField(choices=is_device_status, default=1, null=True, blank=True)
    company = models.ForeignKey("users.Company",null=True,blank=True, on_delete=models.SET_NULL)
    is_deleted = models.BooleanField(default=False,
                                     help_text=('Designates whether this application is deleted'))
    dev_battery = models.CharField(max_length=200, blank=True, null=True)
    dev_solar = models.CharField(max_length=200, blank=True, null=True)
    dev_created_at = models.DateTimeField(auto_now_add=True)
    dev_updated_at = models.DateTimeField(auto_now=True)
    dev_created_by = models.ForeignKey(
        'users.User',
        related_name="device_created_by",
        on_delete=models.SET_NULL, blank=True, null=True
    )
    dev_updated_by = models.ForeignKey(
        'users.User',
        related_name="device_updated_by",
        on_delete=models.SET_NULL, blank=True, null=True
    )
    dev_const_value = models.IntegerField(default=1023)
    def __str__(self):
        return "%s" % self.dev_name


class AmmoniaCatalogValue(models.Model):
    ph_min_value = models.CharField(max_length=255, blank=True, null=True)
    ph_max_value = models.CharField(max_length=255, blank=True, null=True)
    temp_min_value = models.CharField(max_length=255, blank=True, null=True)
    temp_max_value = models.CharField(max_length=255, blank=True, null=True)
    ammonia_value = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = 'Ammonia Value'
        verbose_name_plural = 'Ammonia Value'


class TimeSchedule(models.Model):
    tsl_dev = models.ForeignKey(Device, related_name='device_time_schedule', on_delete=models.SET_NULL, null=True,
                                blank=True)
    tsl_start_time = models.TimeField(null=True, blank=True)
    tsl_end_time = models.TimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Time Schedule'
        verbose_name_plural = 'Time Schedule'

    def __str__(self):
        return "%s" % self.tsl_start_time


class Sensor(models.Model):
    sensor_name = models.CharField(max_length=50)
    sensor_unit = models.CharField(max_length=10, blank=True, null=True)
    sensor_max = models.FloatField(max_length=5)
    sensor_min = models.FloatField(max_length=5)
    sensor_icon = models.ImageField(
        upload_to='uploads/sensor_icon/images/', blank=True, null=True
    )
    def __str__(self) -> str:
        return self.sensor_name

class DeviceData(models.Model):
    dvd_dvg = models.ForeignKey(DeviceGateway, related_name='device_gateway_data', on_delete=models.SET_NULL, null=True,
                                blank=True)
    dvd_dev = models.ForeignKey(Device, related_name='device_data', on_delete=models.SET_NULL, null=True, blank=True)
    dvd_sen = models.ForeignKey("device.Sensor", related_name='sensor_data', on_delete=models.SET_NULL, null=True, blank=True)
    dvd_val = models.CharField(blank=True, null=True, max_length=50)
    dvd_created_at = models.DateTimeField(null=True,blank=True)
    company = models.ForeignKey("users.Company",blank=True, null=True,on_delete=models.SET_NULL)
    device_data_time = models.DateTimeField(null=True,blank=True)
    asset = models.ForeignKey("assets.AssetsProperties",null=True,blank=True,on_delete = models.SET_NULL)
    class Meta:
        verbose_name = 'Device Data'
        verbose_name_plural = 'Device Data'
        indexes = [
                        models.Index(fields=['dvd_sen']),
                        models.Index(fields=['asset']),
                        models.Index(fields=['company']),
                        models.Index(fields=['dvd_dev'])
                    ]

class DeviceDataHistory(models.Model):
    dvd_dvg = models.ForeignKey(DeviceGateway, related_name='device_gateway_data_history', on_delete=models.SET_NULL, null=True,
                                blank=True)
    dvd_dev = models.ForeignKey(Device, related_name='device_data_history', on_delete=models.SET_NULL, null=True, blank=True)
    dvd_sen = models.ForeignKey("device.Sensor", related_name='sensor_data_history', on_delete=models.SET_NULL, null=True, blank=True)
    dvd_val = models.CharField(blank=True, null=True, max_length=50)
    dvd_created_at = models.DateTimeField(null=True,blank=True)
    company = models.ForeignKey("users.Company",blank=True, null=True,on_delete=models.SET_NULL)
    device_data_time = models.DateTimeField(null=True,blank=True)
    asset = models.ForeignKey("assets.AssetsProperties",null=True,blank=True,on_delete = models.SET_NULL)
    class Meta:
        verbose_name = 'Device Data History'
        verbose_name_plural = 'Device Data History'
        indexes = [
                        models.Index(fields=['dvd_sen']),
                        models.Index(fields=['asset']),
                        models.Index(fields=['company']),
                        models.Index(fields=['dvd_dev'])
                    ]

is_status = (
    (0, 'Problem'),
    (1, 'Repairing'),
    (2, 'Observation'),
    (3, 'Solved'),
)

class Camera(models.Model):
    cam_assets = models.ForeignKey('assets.AssetsProperties', related_name='camera_asset', blank=True, null=True,
                                   on_delete=models.SET_NULL)
    cam_status = models.BooleanField(default=True, null=True, blank=True)
    cam_file = models.FileField(upload_to='uploads/camera/file/', blank=True, null=True)
    cam_name = models.CharField(max_length=255, blank=True, null=True)
    cam_brand = models.CharField(max_length=255, blank=True, null=True)
    cam_serial = models.CharField(max_length=255, blank=True, null=True)
    cam_mac = models.CharField(max_length=255, blank=True, null=True)
    cam_ip = models.CharField(max_length=255, blank=True, null=True)
    cam_url = models.TextField(blank=True, null=True)
    cam_port = models.CharField(max_length=255, blank=True, null=True)
    cam_user = models.CharField(max_length=255, blank=True, null=True)
    cam_password = models.CharField(max_length=255, blank=True, null=True)
    cam_location = models.CharField(max_length=255, blank=True, null=True)
    cam_description = models.TextField(blank=True, null=True)
    cam_created_at = models.DateTimeField(auto_now_add=True)
    cam_updated_at = models.DateTimeField(auto_now=True)
    cam_created_by = models.ForeignKey(
        'users.User',
        related_name="camera_created_by",
        on_delete=models.SET_NULL, blank=True, null=True
    )
    cam_updated_by = models.ForeignKey(
        'users.User',
        related_name="camera_updated_by",
        on_delete=models.SET_NULL, blank=True, null=True
    )
    company = models.ForeignKey("users.Company",null=True,blank=True, on_delete=models.SET_NULL)
    def __str__(self):
        return "%s" % self.cam_name


class DeviceRawData(models.Model):
    drd_dev = models.ForeignKey(Device, related_name='device_raw_data', on_delete=models.SET_NULL, null=True, blank=True)
    drd_data = models.TextField(null=True, blank=True)
    drd_created_at = models.DateTimeField(blank=True, null=True)
    gateway = models.ForeignKey("device.DeviceGateway",null=True,blank=True,on_delete=models.SET_NULL)
    company = models.ForeignKey("users.Company",null=True,blank=True, on_delete=models.SET_NULL)
    device_data_time = models.DateTimeField(null=True,blank=True)
    class Meta:
        verbose_name = 'Device Raw Data'
        verbose_name_plural = 'Device Raw Data'


class DeviceControlInfo(models.Model):
    dci_dev = models.ForeignKey(Device, related_name='device_control_info', on_delete=models.SET_NULL, null=True,
                                blank=True)
    dci_data = models.TextField(null=True, blank=True)
    dci_created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Device Control Info'
        verbose_name_plural = 'Device Control Info'


class WeatherReport(models.Model):
    dvd_dev = models.ForeignKey(Device, related_name='device_Weather_data', on_delete=models.SET_NULL, null=True,
                                blank=True)
    weather_temperature = models.CharField(max_length=100, blank=True, null=True)
    weather_description = models.CharField(max_length=100, blank=True, null=True)
    weather_humidity = models.CharField(max_length=100, blank=True, null=True)
    weather_city = models.CharField(max_length=100, blank=True, null=True)
    weather_created_at = models.DateTimeField()


   

class SensorConfiguration(models.Model):
    device = models.ForeignKey("device.Device",null=True,blank=True,on_delete=models.SET_NULL)
    pid = models.IntegerField(blank=True, null=True,validators=[
        MaxValueValidator(255),
        MinValueValidator(1)
    ])
    address = models.IntegerField(blank=True, null=True,validators=[
        MaxValueValidator(255),
        MinValueValidator(0)
    ])
    sensor = models.ForeignKey("device.Sensor",blank=True, null=True, on_delete=models.SET_NULL)
    multiplier = models.FloatField(blank=True, null=True,max_length=10)
    sensor_status = models.IntegerField(choices=is_device_status, default=1, null=True, blank=True)

    def __str__(self) -> str:
        return (self.device.dev_name + self.sensor.sensor_name)

class InvalidValue(models.Model):
    sensor = models.ForeignKey("device.Sensor", on_delete=models.SET_NULL,blank=True, null=True)
    max_invalid_value = models.FloatField(max_length=5)
    min_invalid_value = models.FloatField(max_length=5)
    
    def __str__(self) -> str:
        return self.sensor.sensor_name

class Weather(models.Model):
    weather_temperature = models.DecimalField(default=0,max_digits=5, decimal_places=2)
    weather_description = models.CharField(max_length=100, blank=True, null=True)
    weather_humidity = models.DecimalField(default=0,max_digits=5, decimal_places=2)
    weather_district = models.ForeignKey("assets.District",blank=True, null=True,on_delete=models.SET_NULL)
    weather_created_at = models.DateTimeField()
    sunlight_level = models.CharField(max_length=100,null=True,blank=True)
    solar_radiation = models.DecimalField(default=0,max_digits=5, decimal_places=2)

class UserManualData(models.Model):
        man_assets = models.ForeignKey('assets.AssetsProperties', related_name='man_asset', blank=True, null=True,
                                   on_delete=models.CASCADE)
        man_ph = models.CharField(max_length=200, blank=True, null=True)
        man_ammonia = models.CharField(max_length=200, blank=True, null=True)
        man_DO = models.CharField(max_length=200, blank=True, null=True)
        man_tds = models.CharField(max_length=200, blank=True, null=True)
        man_temperature = models.CharField(max_length=200, blank=True, null=True)
        man_created_at = models.DateTimeField()
        man_updated_at = models.DateTimeField(null=True, blank=True)
        man_created_by = models.ForeignKey(
        'users.User',
        related_name="man_created_by",
        on_delete=models.CASCADE, blank=True, null=True
        )
        class Meta:
            verbose_name = 'Manual User Input'
            verbose_name_plural = 'Manual User Inputs'

class Complain(models.Model):
    class StatusType(models.IntegerChoices):
        CHOOSE_AN_OPTION = '0', _('CHOOSE_AN_OPTION')
        SOLVED = '1', _('SOLVED')
        PENDING = '2', _('PENDING')
        NOT_SOLVED = '3', _('NOT_SOLVED')
        SUBMITTED_FOR_REVIEW = '4', _('SUBMITTED_FOR_REVIEW')

    user = models.ForeignKey('users.User', related_name='user_complain',
                             on_delete=models.CASCADE, blank=True, null=True)
    complain_asset = models.ForeignKey("assets.AssetsProperties",related_name='asset_complain',
                             on_delete=models.CASCADE, blank=True, null=True)
    complain_category = models.CharField(max_length=200, blank=True, null=True)
    complain_title = models.CharField(max_length=200, blank=True, null=True)
    complain_description = models.TextField(blank=True, null=True)
    complain_image = models.ImageField(
        upload_to='uploads/complaint/images/', blank=True, null=True)
    complain_status = models.IntegerField(
        _('complain status'), choices=StatusType.choices, default=StatusType.SUBMITTED_FOR_REVIEW)

    complain_created_at = models.DateField(auto_now_add=True)


class ComplainCategory(models.Model):
    category_name = models.CharField(max_length=200, blank=True, null=True, unique=True)

    def __str__(self):
        return "%s" % self.category_name

from django.db import models

class RetrievedCalibration(models.Model):
    gateway_id = models.BigIntegerField()
    drd_dev_id = models.BigIntegerField()
    ph_value = models.FloatField(null=True, blank=True)
    tds_value = models.FloatField(null=True, blank=True)
    temp_value = models.FloatField(null=True, blank=True)
    ph_calibration = models.FloatField(null=True, blank=True)
    tds_calibration = models.FloatField(null=True, blank=True)
    temp_calibration = models.FloatField(null=True, blank=True)
    manual_ph_value = models.FloatField(null=True, blank=True)
    manual_tds_value = models.FloatField(null=True, blank=True)
    manual_temp_value = models.FloatField(null=True, blank=True)
    calibration_status = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Device Data for Device {self.drd_dev_id} in Gateway {self.gateway_id}"



from django.core.validators import RegexValidator

class Aerator(models.Model):
    device = models.ForeignKey(
        Device,
        related_name='aerators',
        on_delete=models.CASCADE
    )
    aerator_id = models.CharField(
        max_length=100,  # Increased to allow flexible IDs
        help_text='Manually set aerator ID',
        blank=True,
        null=True
    )
    aerator_name = models.CharField(
        max_length=200,
        blank=True, null=True
    )
    mqtt_client_id = models.CharField(
        max_length=64,
        unique=True,
        editable=False,
        help_text='Composite ID used in MQTT topics'
    )
    is_running = models.BooleanField(
        default=False,
        help_text='True if aerator is currently ON/running'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='If False, ignore status updates for this aerator'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        blank=True,
        null=True
    )

    class Meta:
        unique_together = ('device', 'aerator_id')

    def save(self, *args, **kwargs):
        # pad each component:
        # company_id → 3 digits, asset_id → 4 digits, device_id → 4 digits, aerator_id already 2 digits
        company_id = str(self.device.company.id).zfill(3) if self.device.company else '000'
        asset_id   = str(self.device.dev_asset.id).zfill(4) if self.device.dev_asset else '0000'
        device_id  = str(self.device.id).zfill(4)
        # aerator_id is e.g. "01"
        numeric_mqtt_id = re.sub(r'\D', '', self.aerator_id)

        self.mqtt_client_id = f"{numeric_mqtt_id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.device.dev_name} ▸ Aerator {self.aerator_id}"


from django.utils.timezone import now

class AeratorStatusLog(models.Model):
    """
    Every time an aerator reports status, we keep a history.
    """
    aerator = models.ForeignKey(
        Aerator,
        related_name='status_logs',
        on_delete=models.CASCADE
    )
    was_running = models.BooleanField(
        help_text="True if the aerator was ON at this timestamp",
        blank=True,
        null=True
    )
    timestamp = models.DateTimeField(
        default=now,
        help_text="When this status was recorded",
        blank=True,
        null=True
    )

    def __str__(self):
        state = "ON" if self.was_running else "OFF"
        return f"{self.aerator} @ {self.timestamp:%Y-%m-%d %H:%M:%S} → {state}"


class AeratorCommandLog(models.Model):
    """
    Logs each command sent to an aerator, so ACKs can be correlated across restarts.
    """
    aerator = models.ForeignKey(
        'Aerator',
        related_name='command_logs',
        on_delete=models.CASCADE
    )
    command_on = models.BooleanField(
        help_text="True if this command is to turn the aerator ON"
    )
    sent_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the command was published to MQTT"
    )
    acked = models.BooleanField(
        default=False,
        help_text="Whether we received the 'executed' ack for this command"
    )
    acked_at   = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When the 'executed' ack was received"
    )

    class Meta:
        ordering = ['-sent_at']
        get_latest_by = 'sent_at'

    def __str__(self):
        state = 'ON' if self.command_on else 'OFF'
        return f"Cmd({state})→{self.aerator} @ {self.sent_at:%Y-%m-%d %H:%M:%S}"




@receiver(post_save, sender=DeviceRawData)
def post_save_raw_data(sender,instance:DeviceRawData,created, **kwargs):
    from device.tasks import save_device_data
    
    if created:
        try:
            raw_data = json.loads(instance.drd_data)
            # for data in raw_data["content"]:
            save_device_data.delay(raw_data = raw_data["content"],drd_dev_id=instance.drd_dev_id,gateway_id = instance.gateway_id)
            
        except Exception:
            traceback.print_exc()                                                                
